import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from .models import AuditLog
from .database import AsyncSessionLocal

class AuditService:
    """Service for logging security and audit events"""
    
    async def log_security_event(
        self,
        event_type: str,
        description: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        endpoint: Optional[str] = None,
        request_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        severity: str = "info"
    ):
        """Log a security event to the audit log"""
        async with AsyncSessionLocal() as db:
            try:
                audit_log = AuditLog(
                    user_id=uuid.UUID(user_id) if user_id else None,
                    event_type=event_type,
                    event_description=description,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    endpoint=endpoint,
                    request_id=request_id,
                    metadata=json.dumps(metadata) if metadata else None,
                    severity=severity
                )
                
                db.add(audit_log)
                await db.commit()
                
            except Exception as e:
                # Don't let audit logging failures break the main flow
                print(f"Failed to log audit event: {e}")
                await db.rollback()

    async def log_authentication_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        email: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        failure_reason: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """Log authentication-related events"""
        description = f"Authentication event: {event_type}"
        if email:
            description += f" for {email}"
        
        metadata = {
            "success": success,
            "email": email
        }
        
        if failure_reason:
            metadata["failure_reason"] = failure_reason
        
        severity = "info" if success else "warning"
        
        await self.log_security_event(
            event_type=event_type,
            description=description,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            metadata=metadata,
            severity=severity
        )

    async def log_authorization_event(
        self,
        event_type: str,
        user_id: str,
        resource: str,
        action: str,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """Log authorization-related events"""
        description = f"Authorization {event_type}: {action} on {resource}"
        
        metadata = {
            "resource": resource,
            "action": action,
            "success": success
        }
        
        severity = "info" if success else "warning"
        
        await self.log_security_event(
            event_type=event_type,
            description=description,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            metadata=metadata,
            severity=severity
        )

    async def log_data_access_event(
        self,
        event_type: str,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """Log data access events"""
        description = f"Data access: {action} on {resource_type} {resource_id}"
        
        metadata = {
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": action
        }
        
        await self.log_security_event(
            event_type=event_type,
            description=description,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            metadata=metadata,
            severity="info"
        )

    async def log_system_event(
        self,
        event_type: str,
        description: str,
        severity: str = "info",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log system-level events"""
        await self.log_security_event(
            event_type=event_type,
            description=description,
            severity=severity,
            metadata=metadata
        )

    async def get_audit_logs(
        self,
        db: AsyncSession,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[AuditLog]:
        """Retrieve audit logs with filtering"""
        query = select(AuditLog)
        
        if user_id:
            query = query.where(AuditLog.user_id == uuid.UUID(user_id))
        
        if event_type:
            query = query.where(AuditLog.event_type == event_type)
        
        if severity:
            query = query.where(AuditLog.severity == severity)
        
        if start_date:
            query = query.where(AuditLog.created_at >= start_date)
        
        if end_date:
            query = query.where(AuditLog.created_at <= end_date)
        
        query = query.order_by(AuditLog.created_at.desc())
        query = query.offset(offset).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()

    async def get_security_summary(
        self,
        db: AsyncSession,
        user_id: Optional[str] = None,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Get security event summary for the last N hours"""
        from sqlalchemy import func
        
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        query = select(
            AuditLog.event_type,
            AuditLog.severity,
            func.count(AuditLog.id).label('count')
        ).where(
            AuditLog.created_at >= start_time
        )
        
        if user_id:
            query = query.where(AuditLog.user_id == uuid.UUID(user_id))
        
        query = query.group_by(AuditLog.event_type, AuditLog.severity)
        
        result = await db.execute(query)
        events = result.all()
        
        summary = {
            "period_hours": hours,
            "total_events": sum(event.count for event in events),
            "events_by_type": {},
            "events_by_severity": {}
        }
        
        for event in events:
            # Group by event type
            if event.event_type not in summary["events_by_type"]:
                summary["events_by_type"][event.event_type] = 0
            summary["events_by_type"][event.event_type] += event.count
            
            # Group by severity
            if event.severity not in summary["events_by_severity"]:
                summary["events_by_severity"][event.severity] = 0
            summary["events_by_severity"][event.severity] += event.count
        
        return summary

# Global audit service instance
audit_service = AuditService()