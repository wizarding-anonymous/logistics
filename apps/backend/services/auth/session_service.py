import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from .models import UserSession
from .redis_client import get_redis
from .audit_service import audit_service

class SessionService:
    """Service for managing user sessions"""
    
    MAX_CONCURRENT_SESSIONS = 5  # Maximum concurrent sessions per user
    SESSION_TIMEOUT_HOURS = 24   # Session timeout in hours
    
    async def create_session(
        self,
        db: AsyncSession,
        user_id: str,
        token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserSession:
        """Create a new user session"""
        
        # Clean up expired sessions first
        await self._cleanup_expired_sessions(db, user_id)
        
        # Check concurrent session limit
        await self._enforce_session_limit(db, user_id)
        
        # Create token hash for storage
        token_hash = self._hash_token(token)
        
        # Create session record
        session = UserSession(
            user_id=uuid.UUID(user_id),
            token_hash=token_hash,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.utcnow() + timedelta(hours=self.SESSION_TIMEOUT_HOURS)
        )
        
        db.add(session)
        await db.commit()
        await db.refresh(session)
        
        # Store session in Redis for fast access
        redis = await get_redis()
        session_data = {
            "user_id": user_id,
            "session_id": str(session.id),
            "ip_address": ip_address,
            "user_agent": user_agent,
            "created_at": session.created_at.isoformat(),
            "expires_at": session.expires_at.isoformat()
        }
        
        await redis.store_session(
            str(session.id),
            session_data,
            int(timedelta(hours=self.SESSION_TIMEOUT_HOURS).total_seconds())
        )
        
        # Log session creation
        await audit_service.log_security_event(
            event_type="SESSION_CREATED",
            description="New user session created",
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={"session_id": str(session.id)}
        )
        
        return session

    async def get_session(
        self,
        db: AsyncSession,
        session_id: str
    ) -> Optional[UserSession]:
        """Get session by ID"""
        
        # Try Redis first for performance
        redis = await get_redis()
        session_data = await redis.get_session(session_id)
        
        if session_data:
            # Update last activity in Redis
            session_data["last_activity"] = datetime.utcnow().isoformat()
            await redis.store_session(
                session_id,
                session_data,
                int(timedelta(hours=self.SESSION_TIMEOUT_HOURS).total_seconds())
            )
        
        # Get from database
        result = await db.execute(
            select(UserSession).where(
                UserSession.id == uuid.UUID(session_id),
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow()
            )
        )
        
        session = result.scalars().first()
        
        if session:
            # Update last activity
            session.last_activity = datetime.utcnow()
            await db.commit()
        
        return session

    async def validate_session(
        self,
        db: AsyncSession,
        token: str
    ) -> Optional[UserSession]:
        """Validate session by token"""
        
        token_hash = self._hash_token(token)
        
        result = await db.execute(
            select(UserSession).where(
                UserSession.token_hash == token_hash,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow()
            )
        )
        
        session = result.scalars().first()
        
        if session:
            # Update last activity
            session.last_activity = datetime.utcnow()
            await db.commit()
            
            # Update Redis cache
            redis = await get_redis()
            session_data = await redis.get_session(str(session.id))
            if session_data:
                session_data["last_activity"] = datetime.utcnow().isoformat()
                await redis.store_session(
                    str(session.id),
                    session_data,
                    int(timedelta(hours=self.SESSION_TIMEOUT_HOURS).total_seconds())
                )
        
        return session

    async def revoke_session(
        self,
        db: AsyncSession,
        session_id: str,
        user_id: Optional[str] = None
    ) -> bool:
        """Revoke a specific session"""
        
        query = select(UserSession).where(UserSession.id == uuid.UUID(session_id))
        if user_id:
            query = query.where(UserSession.user_id == uuid.UUID(user_id))
        
        result = await db.execute(query)
        session = result.scalars().first()
        
        if not session:
            return False
        
        # Mark as inactive
        session.is_active = False
        await db.commit()
        
        # Remove from Redis
        redis = await get_redis()
        await redis.delete_session(session_id)
        
        # Log session revocation
        await audit_service.log_security_event(
            event_type="SESSION_REVOKED",
            description="User session revoked",
            user_id=str(session.user_id),
            metadata={"session_id": session_id}
        )
        
        return True

    async def revoke_all_user_sessions(
        self,
        db: AsyncSession,
        user_id: str,
        except_session_id: Optional[str] = None
    ) -> int:
        """Revoke all sessions for a user"""
        
        query = select(UserSession).where(
            UserSession.user_id == uuid.UUID(user_id),
            UserSession.is_active == True
        )
        
        if except_session_id:
            query = query.where(UserSession.id != uuid.UUID(except_session_id))
        
        result = await db.execute(query)
        sessions = result.scalars().all()
        
        revoked_count = 0
        redis = await get_redis()
        
        for session in sessions:
            session.is_active = False
            await redis.delete_session(str(session.id))
            revoked_count += 1
        
        await db.commit()
        
        # Log bulk session revocation
        await audit_service.log_security_event(
            event_type="ALL_SESSIONS_REVOKED",
            description=f"All user sessions revoked ({revoked_count} sessions)",
            user_id=user_id,
            metadata={"revoked_count": revoked_count, "except_session": except_session_id}
        )
        
        return revoked_count

    async def get_user_sessions(
        self,
        db: AsyncSession,
        user_id: str,
        active_only: bool = True
    ) -> List[UserSession]:
        """Get all sessions for a user"""
        
        query = select(UserSession).where(UserSession.user_id == uuid.UUID(user_id))
        
        if active_only:
            query = query.where(
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow()
            )
        
        query = query.order_by(UserSession.last_activity.desc())
        
        result = await db.execute(query)
        return result.scalars().all()

    async def cleanup_expired_sessions(self, db: AsyncSession) -> int:
        """Clean up expired sessions (should be run periodically)"""
        
        # Delete expired sessions from database
        result = await db.execute(
            delete(UserSession).where(
                UserSession.expires_at < datetime.utcnow()
            )
        )
        
        deleted_count = result.rowcount
        await db.commit()
        
        # Log cleanup
        if deleted_count > 0:
            await audit_service.log_system_event(
                event_type="SESSION_CLEANUP",
                description=f"Cleaned up {deleted_count} expired sessions",
                metadata={"deleted_count": deleted_count}
            )
        
        return deleted_count

    async def get_session_stats(
        self,
        db: AsyncSession,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get session statistics"""
        from sqlalchemy import func
        
        query = select(
            func.count(UserSession.id).label('total_sessions'),
            func.count(UserSession.id).filter(UserSession.is_active == True).label('active_sessions'),
            func.count(UserSession.id).filter(UserSession.expires_at > datetime.utcnow()).label('valid_sessions')
        )
        
        if user_id:
            query = query.where(UserSession.user_id == uuid.UUID(user_id))
        
        result = await db.execute(query)
        stats = result.first()
        
        return {
            "total_sessions": stats.total_sessions,
            "active_sessions": stats.active_sessions,
            "valid_sessions": stats.valid_sessions
        }

    def _hash_token(self, token: str) -> str:
        """Create a hash of the token for storage"""
        return hashlib.sha256(token.encode()).hexdigest()

    async def _cleanup_expired_sessions(self, db: AsyncSession, user_id: str):
        """Clean up expired sessions for a specific user"""
        await db.execute(
            delete(UserSession).where(
                UserSession.user_id == uuid.UUID(user_id),
                UserSession.expires_at < datetime.utcnow()
            )
        )
        await db.commit()

    async def _enforce_session_limit(self, db: AsyncSession, user_id: str):
        """Enforce maximum concurrent sessions limit"""
        
        from sqlalchemy import func
        
        # Get active sessions count
        result = await db.execute(
            select(func.count(UserSession.id)).where(
                UserSession.user_id == uuid.UUID(user_id),
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow()
            )
        )
        
        active_count = result.scalar()
        
        if active_count >= self.MAX_CONCURRENT_SESSIONS:
            # Revoke oldest sessions to make room
            oldest_sessions = await db.execute(
                select(UserSession).where(
                    UserSession.user_id == uuid.UUID(user_id),
                    UserSession.is_active == True,
                    UserSession.expires_at > datetime.utcnow()
                ).order_by(UserSession.last_activity.asc()).limit(
                    active_count - self.MAX_CONCURRENT_SESSIONS + 1
                )
            )
            
            redis = await get_redis()
            for session in oldest_sessions.scalars():
                session.is_active = False
                await redis.delete_session(str(session.id))
            
            await db.commit()

# Global session service instance
session_service = SessionService()