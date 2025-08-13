import time
import hashlib
from typing import Dict, Optional, Callable
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from .redis_client import get_redis
from .audit_service import audit_service

class RateLimitConfig:
    """Rate limit configuration for different endpoints"""
    
    # Default limits (requests per minute)
    DEFAULT_LIMIT = 60
    
    # Endpoint-specific limits
    ENDPOINT_LIMITS = {
        "/api/v1/auth/token": 5,  # Login attempts
        "/api/v1/auth/token/2fa": 5,  # 2FA login attempts
        "/api/v1/auth/register": 3,  # Registration attempts
        "/api/v1/auth/2fa/setup": 2,  # 2FA setup
        "/api/v1/auth/2fa/enable": 5,  # 2FA enable attempts
    }
    
    # IP-based limits (requests per minute)
    IP_LIMITS = {
        "/api/v1/auth/token": 10,  # Total login attempts per IP
        "/api/v1/auth/register": 5,  # Total registration attempts per IP
    }

class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis"""
    
    def __init__(self, app, config: RateLimitConfig = None):
        super().__init__(app)
        self.config = config or RateLimitConfig()

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks and non-auth endpoints
        if not request.url.path.startswith("/api/v1/auth") or request.url.path == "/health":
            return await call_next(request)

        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check IP-based rate limits first
        ip_blocked = await self._check_ip_rate_limit(request, client_ip)
        if ip_blocked:
            return ip_blocked

        # Check endpoint-specific rate limits
        endpoint_blocked = await self._check_endpoint_rate_limit(request, client_ip)
        if endpoint_blocked:
            return endpoint_blocked

        # Continue with request
        response = await call_next(request)
        return response

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"

    async def _check_ip_rate_limit(self, request: Request, client_ip: str) -> Optional[JSONResponse]:
        """Check IP-based rate limits"""
        endpoint = request.url.path
        
        if endpoint not in self.config.IP_LIMITS:
            return None

        limit = self.config.IP_LIMITS[endpoint]
        identifier = f"ip:{client_ip}:{endpoint}"
        
        redis = await get_redis()
        is_allowed, current_count, ttl = await redis.check_rate_limit(
            identifier, limit, 60  # 1 minute window
        )
        
        if not is_allowed:
            await audit_service.log_security_event(
                event_type="RATE_LIMIT_EXCEEDED",
                description=f"IP rate limit exceeded for {endpoint}",
                ip_address=client_ip,
                endpoint=endpoint,
                metadata={"limit": limit, "current_count": current_count}
            )
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "message": f"Too many requests from IP. Limit: {limit} per minute",
                    "retry_after": ttl
                },
                headers={"Retry-After": str(ttl)}
            )
        
        return None

    async def _check_endpoint_rate_limit(self, request: Request, client_ip: str) -> Optional[JSONResponse]:
        """Check endpoint-specific rate limits"""
        endpoint = request.url.path
        
        # Get user identifier if authenticated
        user_id = await self._get_user_id_from_token(request)
        
        if user_id:
            identifier = f"user:{user_id}:{endpoint}"
        else:
            identifier = f"ip:{client_ip}:{endpoint}"
        
        limit = self.config.ENDPOINT_LIMITS.get(endpoint, self.config.DEFAULT_LIMIT)
        
        redis = await get_redis()
        is_allowed, current_count, ttl = await redis.check_rate_limit(
            identifier, limit, 60  # 1 minute window
        )
        
        if not is_allowed:
            await audit_service.log_security_event(
                event_type="RATE_LIMIT_EXCEEDED",
                description=f"Endpoint rate limit exceeded for {endpoint}",
                user_id=user_id,
                ip_address=client_ip,
                endpoint=endpoint,
                metadata={"limit": limit, "current_count": current_count}
            )
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "message": f"Too many requests to {endpoint}. Limit: {limit} per minute",
                    "retry_after": ttl
                },
                headers={"Retry-After": str(ttl)}
            )
        
        return None

    async def _get_user_id_from_token(self, request: Request) -> Optional[str]:
        """Extract user ID from JWT token if present"""
        try:
            from .security import decode_token
            
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None
            
            token = auth_header.split(" ")[1]
            payload = decode_token(token)
            
            if payload:
                return payload.get("sub")
        except Exception:
            pass
        
        return None


class RateLimiter:
    """Utility class for manual rate limiting checks"""
    
    @staticmethod
    async def check_login_attempts(identifier: str, max_attempts: int = 5, window_minutes: int = 15) -> tuple[bool, int]:
        """
        Check failed login attempts for user/IP
        Returns: (is_allowed, remaining_attempts)
        """
        redis = await get_redis()
        key = f"login_attempts:{identifier}"
        
        current_attempts = await redis.get(key)
        current_attempts = int(current_attempts) if current_attempts else 0
        
        if current_attempts >= max_attempts:
            return False, 0
        
        return True, max_attempts - current_attempts

    @staticmethod
    async def record_failed_login(identifier: str, window_minutes: int = 15):
        """Record a failed login attempt"""
        redis = await get_redis()
        key = f"login_attempts:{identifier}"
        
        current_attempts = await redis.incr(key)
        if current_attempts == 1:
            await redis.expire(key, window_minutes * 60)

    @staticmethod
    async def clear_login_attempts(identifier: str):
        """Clear failed login attempts after successful login"""
        redis = await get_redis()
        key = f"login_attempts:{identifier}"
        await redis.delete(key)

    @staticmethod
    async def is_account_locked(user_id: str) -> tuple[bool, Optional[int]]:
        """
        Check if account is temporarily locked
        Returns: (is_locked, seconds_until_unlock)
        """
        redis = await get_redis()
        key = f"account_lock:{user_id}"
        
        lock_data = await redis.get(key)
        if not lock_data:
            return False, None
        
        ttl = await redis.ttl(key)
        return True, ttl if ttl > 0 else None

    @staticmethod
    async def lock_account(user_id: str, duration_minutes: int = 30):
        """Temporarily lock account"""
        redis = await get_redis()
        key = f"account_lock:{user_id}"
        await redis.set(key, "locked", duration_minutes * 60)

    @staticmethod
    async def unlock_account(user_id: str):
        """Unlock account"""
        redis = await get_redis()
        key = f"account_lock:{user_id}"
        await redis.delete(key)