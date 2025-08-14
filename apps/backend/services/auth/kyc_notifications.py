import asyncio
import logging
from typing import Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class KYCNotificationService:
    """Service for sending KYC-related notifications"""
    
    @staticmethod
    async def send_document_uploaded_notification(user_email: str, document_type: str):
        """Send notification when a KYC document is uploaded"""
        try:
            # In production, this would integrate with the notifications service
            # For now, we'll log the notification
            logger.info(f"KYC Document uploaded notification sent to {user_email} for {document_type}")
            
            # Mock email sending
            await asyncio.sleep(0.1)
            
            # In production, send to Kafka topic for notifications service
            notification_data = {
                "type": "kyc_document_uploaded",
                "recipient": user_email,
                "template": "kyc_document_uploaded",
                "data": {
                    "document_type": document_type,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            # TODO: Send to Kafka notifications topic
            logger.info(f"KYC notification queued: {json.dumps(notification_data)}")
            
        except Exception as e:
            logger.error(f"Failed to send document uploaded notification: {e}")
    
    @staticmethod
    async def send_document_approved_notification(user_email: str, document_type: str):
        """Send notification when a KYC document is approved"""
        try:
            logger.info(f"KYC Document approved notification sent to {user_email} for {document_type}")
            
            await asyncio.sleep(0.1)
            
            notification_data = {
                "type": "kyc_document_approved",
                "recipient": user_email,
                "template": "kyc_document_approved",
                "data": {
                    "document_type": document_type,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            logger.info(f"KYC notification queued: {json.dumps(notification_data)}")
            
        except Exception as e:
            logger.error(f"Failed to send document approved notification: {e}")
    
    @staticmethod
    async def send_document_rejected_notification(user_email: str, document_type: str, rejection_reason: str):
        """Send notification when a KYC document is rejected"""
        try:
            logger.info(f"KYC Document rejected notification sent to {user_email} for {document_type}")
            
            await asyncio.sleep(0.1)
            
            notification_data = {
                "type": "kyc_document_rejected",
                "recipient": user_email,
                "template": "kyc_document_rejected",
                "data": {
                    "document_type": document_type,
                    "rejection_reason": rejection_reason,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            logger.info(f"KYC notification queued: {json.dumps(notification_data)}")
            
        except Exception as e:
            logger.error(f"Failed to send document rejected notification: {e}")
    
    @staticmethod
    async def send_kyc_completed_notification(user_email: str):
        """Send notification when KYC process is completed"""
        try:
            logger.info(f"KYC Completed notification sent to {user_email}")
            
            await asyncio.sleep(0.1)
            
            notification_data = {
                "type": "kyc_completed",
                "recipient": user_email,
                "template": "kyc_completed",
                "data": {
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            logger.info(f"KYC notification queued: {json.dumps(notification_data)}")
            
        except Exception as e:
            logger.error(f"Failed to send KYC completed notification: {e}")
    
    @staticmethod
    async def send_validation_failed_notification(user_email: str, document_type: str, validation_errors: list):
        """Send notification when document validation fails"""
        try:
            logger.info(f"KYC Validation failed notification sent to {user_email} for {document_type}")
            
            await asyncio.sleep(0.1)
            
            notification_data = {
                "type": "kyc_validation_failed",
                "recipient": user_email,
                "template": "kyc_validation_failed",
                "data": {
                    "document_type": document_type,
                    "validation_errors": validation_errors,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            logger.info(f"KYC notification queued: {json.dumps(notification_data)}")
            
        except Exception as e:
            logger.error(f"Failed to send validation failed notification: {e}")

# Global notification service instance
kyc_notification_service = KYCNotificationService()