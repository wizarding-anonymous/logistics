import logging
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, List, Optional

from ... import schemas, service, security, models
from ...database import get_db

router = APIRouter()
audit_logger = logging.getLogger('audit')
logger = logging.getLogger(__name__)

# This tells FastAPI where to get the token from
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

import uuid

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> models.User:
    """
    Dependency to get the current user from a JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = security.decode_token(token)
    if payload is None:
        raise credentials_exception

    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise credentials_exception

    user = await service.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise credentials_exception

    # Check if the token was issued before the user's tokens were revoked
    if user.tokens_revoked_at:
        token_issued_at = datetime.fromtimestamp(payload.get("iat", 0))
        if token_issued_at < user.tokens_revoked_at:
            raise credentials_exception

    return user

@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: schemas.UserCreate, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Register a new user after verifying reCAPTCHA.
    """
    extra_log = {"client_ip": request.client.host, "email": user_in.email}
    if not await security.verify_recaptcha(user_in.recaptcha_token):
        audit_logger.warning("Registration failed: Invalid reCAPTCHA", extra=extra_log)
        raise HTTPException(status_code=400, detail="Invalid reCAPTCHA token.")

    db_user = await service.get_user_by_email(db, email=user_in.email)
    if db_user:
        audit_logger.warning("Registration failed: Email already registered", extra=extra_log)
        raise HTTPException(status_code=400, detail="Email already registered")

    created_user = await service.create_user(db=db, user=user_in)
    audit_logger.info("User registered successfully", extra={"user_id": str(created_user.id), **extra_log})
    return created_user

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    OAuth2-compatible endpoint to get an access token.
    If TFA is enabled, this will fail and the client must use /token/2fa.
    """
    extra_log = {"client_ip": request.client.host, "username": form_data.username}
    user = await service.authenticate_user(db, username=form_data.username, password=form_data.password)
    if not user:
        audit_logger.warning("Login failed: Invalid credentials", extra=extra_log)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.is_tfa_enabled:
        audit_logger.info("Login requires TFA", extra={"user_id": str(user.id), **extra_log})
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="TFA is enabled for this account. Please use the /token/2fa endpoint.",
        )

    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "roles": user.roles or [],
        "scopes": form_data.scopes or [],
    }
    access_token = security.create_access_token(data=token_data)
    refresh_token = security.create_refresh_token(data={"sub": str(user.id)})

    audit_logger.info("Login successful (no TFA)", extra={"user_id": str(user.id), **extra_log})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/token/2fa", response_model=schemas.Token)
async def login_for_access_token_with_tfa(
    request: Request, form_data: schemas.TokenRequestWithTFA, db: AsyncSession = Depends(get_db)
):
    """
    Get an access token for a user with TFA enabled.
    Supports both TOTP codes and backup codes.
    """
    extra_log = {"client_ip": request.client.host, "username": form_data.username}
    user = await service.authenticate_user(db, username=form_data.username, password=form_data.password)
    if not user:
        audit_logger.warning("Login failed (TFA): Invalid credentials", extra=extra_log)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not user.is_tfa_enabled or not user.tfa_secret:
        audit_logger.warning("Login failed (TFA): TFA not enabled", extra={"user_id": str(user.id), **extra_log})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TFA is not enabled for this account.",
        )

    # Verify either TOTP code or backup code
    auth_valid = False
    auth_method = ""
    
    if form_data.tfa_code:
        auth_valid = security.verify_tfa_code(secret=user.tfa_secret, code=form_data.tfa_code)
        auth_method = "totp"
    elif form_data.backup_code:
        auth_valid = await service.verify_backup_code(db, user.id, form_data.backup_code)
        auth_method = "backup_code"
    
    if not auth_valid:
        audit_logger.warning(f"Login failed (TFA): Invalid {auth_method}", extra={"user_id": str(user.id), **extra_log})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication code.",
        )

    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "roles": user.roles or [],
        "scopes": [],
    }
    access_token = security.create_access_token(data=token_data)
    refresh_token = security.create_refresh_token(data={"sub": str(user.id)})

    audit_logger.info(f"Login successful (TFA-{auth_method})", extra={"user_id": str(user.id), **extra_log})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    """
    Fetch the currently authenticated user.
    """
    return current_user

# =================================
# KYC Routes
# =================================

@router.post("/users/me/kyc-documents/upload-url", response_model=dict)
async def get_kyc_upload_url(
    upload_request: schemas.KYCDocumentUploadRequest,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a presigned URL for uploading a KYC document.
    """
    if "supplier" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only users with the 'supplier' role can submit KYC documents."
        )
    
    from ...s3_client import s3_client
    
    # Generate unique file key
    file_key = s3_client.generate_file_key(
        str(current_user.id), 
        upload_request.document_type, 
        upload_request.file_name
    )
    
    # Generate presigned URL for upload
    upload_url = s3_client.generate_presigned_url(
        file_key, 
        expiration=3600,  # 1 hour
        http_method='PUT'
    )
    
    if not upload_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate upload URL"
        )
    
    return {
        "upload_url": upload_url,
        "file_key": file_key,
        "expires_in": 3600
    }

@router.post("/users/me/kyc-documents", response_model=schemas.KYCDocument, status_code=status.HTTP_201_CREATED)
async def submit_kyc_document(
    doc_in: schemas.KYCDocumentCreate,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit a KYC document after uploading the file.
    This creates the database record and triggers validation.
    """
    if "supplier" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only users with the 'supplier' role can submit KYC documents."
        )
    
    try:
        # Create the document record
        document = await service.create_kyc_document(db=db, user_id=current_user.id, doc_in=doc_in)
        
        # Trigger async validation
        from ...file_validator import FileValidator
        from ...s3_client import s3_client
        import asyncio
        
        async def validate_document():
            try:
                # Download file for validation
                file_content, error = await s3_client.download_file(doc_in.file_storage_key)
                if error:
                    logger.error(f"Failed to download file for validation: {error}")
                    return
                
                # Validate the document
                validation_results = await FileValidator.validate_document(
                    file_content, doc_in.file_name, doc_in.document_type
                )
                
                # Update document with validation results
                await service.process_kyc_document_validation(db, document.id, validation_results)
                
                # Send notification if validation failed
                if validation_results.get('validation_errors'):
                    # TODO: Send notification to user about validation failure
                    pass
                
            except Exception as e:
                logger.error(f"Error during document validation: {e}")
        
        # Start validation in background
        asyncio.create_task(validate_document())
        
        return document
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/users/me/kyc-documents", response_model=List[schemas.KYCDocument])
async def list_my_kyc_documents(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all KYC documents for the currently authenticated user.
    """
    return await service.get_kyc_documents_by_user(db=db, user_id=current_user.id)

@router.get("/users/me/kyc-status", response_model=dict)
async def get_my_kyc_status(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get overall KYC status for the current user.
    """
    return await service.get_user_kyc_status(db=db, user_id=current_user.id)

@router.get("/users/me/kyc-documents/{doc_id}/download-url", response_model=dict)
async def get_kyc_download_url(
    doc_id: uuid.UUID,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a presigned URL for downloading a KYC document.
    """
    document = await service.get_kyc_document_by_id(db, doc_id)
    if not document or document.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    from ...s3_client import s3_client
    
    download_url = s3_client.generate_presigned_url(
        document.file_storage_key,
        expiration=3600,  # 1 hour
        http_method='GET'
    )
    
    if not download_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate download URL"
        )
    
    return {
        "download_url": download_url,
        "file_name": document.file_name,
        "expires_in": 3600
    }


# =================================
# Two-Factor Authentication Routes
# =================================

@router.post("/2fa/setup", response_model=schemas.TFASetupResponse)
async def setup_tfa(
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate and return a TFA secret, provisioning URI, and backup codes for the user.
    The secret is stored temporarily but not yet active.
    """
    extra_log = {"client_ip": request.client.host, "user_id": str(current_user.id)}
    if current_user.is_tfa_enabled:
        audit_logger.warning("TFA setup failed: already enabled", extra=extra_log)
        raise HTTPException(status_code=400, detail="TFA is already enabled.")

    secret = security.generate_tfa_secret()
    await service.set_user_tfa_secret(db, user_id=current_user.id, secret=secret)
    
    # Generate backup codes
    backup_codes = await service.generate_backup_codes(db, current_user.id)

    uri = security.generate_tfa_provisioning_uri(current_user.email, secret)
    audit_logger.info("TFA setup initiated", extra=extra_log)
    return {"secret": secret, "provisioning_uri": uri, "backup_codes": backup_codes}

@router.post("/2fa/enable", status_code=status.HTTP_200_OK)
async def enable_tfa(
    request: Request,
    tfa_data: schemas.TFAEnableRequest,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Verify the TOTP code and enable TFA for the user.
    """
    extra_log = {"client_ip": request.client.host, "user_id": str(current_user.id)}
    if current_user.is_tfa_enabled:
        raise HTTPException(status_code=400, detail="TFA is already enabled.")
    if not current_user.tfa_secret:
        raise HTTPException(status_code=400, detail="TFA secret not found. Please run setup first.")

    is_valid = security.verify_tfa_code(secret=current_user.tfa_secret, code=tfa_data.code)
    if not is_valid:
        audit_logger.warning("TFA enable failed: Invalid code", extra=extra_log)
        raise HTTPException(status_code=400, detail="Invalid TFA code.")

    await service.set_user_tfa_enabled(db, user_id=current_user.id, enabled=True)
    audit_logger.info("TFA enabled successfully", extra=extra_log)
    return {"message": "TFA enabled successfully."}


@router.post("/2fa/disable", status_code=status.HTTP_200_OK)
async def disable_tfa(
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Disable TFA for the user.
    """
    extra_log = {"client_ip": request.client.host, "user_id": str(current_user.id)}
    if not current_user.is_tfa_enabled:
        raise HTTPException(status_code=400, detail="TFA is not currently enabled.")

    await service.set_user_tfa_enabled(db, user_id=current_user.id, enabled=False)
    await service.set_user_tfa_secret(db, user_id=current_user.id, secret=None)
    audit_logger.info("TFA disabled successfully", extra=extra_log)
    return {"message": "TFA disabled successfully."}

# =================================
# Session Management Routes
# =================================

@router.get("/sessions", response_model=schemas.SessionListResponse)
async def list_user_sessions(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all active sessions for the current user.
    """
    from ...session_service import session_service
    
    sessions = await session_service.get_user_sessions(db, str(current_user.id))
    active_sessions = [s for s in sessions if s.is_active]
    
    return {
        "sessions": sessions,
        "total_count": len(sessions),
        "active_count": len(active_sessions)
    }

@router.delete("/sessions/{session_id}", status_code=status.HTTP_200_OK)
async def revoke_session(
    session_id: str,
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Revoke a specific session.
    """
    from ...session_service import session_service
    
    extra_log = {"client_ip": request.client.host, "user_id": str(current_user.id), "session_id": session_id}
    
    success = await session_service.revoke_session(db, session_id, str(current_user.id))
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    audit_logger.info("User session revoked", extra=extra_log)
    return {"message": "Session has been revoked."}

@router.post("/sessions/revoke-all", status_code=status.HTTP_200_OK)
async def revoke_all_sessions(
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Revoke all active sessions for the current user.
    """
    from ...session_service import session_service
    
    extra_log = {"client_ip": request.client.host, "user_id": str(current_user.id)}
    
    revoked_count = await session_service.revoke_all_user_sessions(db, str(current_user.id))
    audit_logger.info(f"All user sessions revoked ({revoked_count})", extra=extra_log)
    return {"message": f"All {revoked_count} sessions have been revoked. Please log in again."}

# =================================
# Password Management Routes
# =================================

@router.post("/password/change", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: schemas.PasswordChangeRequest,
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Change user password.
    """
    extra_log = {"client_ip": request.client.host, "user_id": str(current_user.id)}
    
    result = await service.change_password(
        db, current_user.id, password_data.current_password, password_data.new_password
    )
    
    if not result:
        audit_logger.warning("Password change failed: Invalid current password", extra=extra_log)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    audit_logger.info("Password changed successfully", extra=extra_log)
    return {"message": "Password changed successfully. Please log in again."}

# =================================
# Backup Codes Routes
# =================================

@router.post("/2fa/backup-codes/regenerate", response_model=List[str])
async def regenerate_backup_codes(
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Regenerate backup codes for 2FA.
    """
    extra_log = {"client_ip": request.client.host, "user_id": str(current_user.id)}
    
    if not current_user.is_tfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled for this account"
        )
    
    backup_codes = await service.generate_backup_codes(db, current_user.id)
    audit_logger.info("Backup codes regenerated", extra=extra_log)
    
    return backup_codes

@router.get("/2fa/backup-codes/count")
async def get_backup_codes_count(
    current_user: models.User = Depends(get_current_user),
):
    """
    Get the number of remaining backup codes.
    """
    if not current_user.is_tfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled for this account"
        )
    
    remaining_count = len(current_user.backup_codes) if current_user.backup_codes else 0
    return {"remaining_backup_codes": remaining_count}

# =================================
# Profile Management Routes
# =================================

@router.put("/users/me/profile", response_model=schemas.User)
async def update_profile(
    profile_data: dict,
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user profile information.
    """
    extra_log = {"client_ip": request.client.host, "user_id": str(current_user.id)}
    
    updated_user = await service.update_user_profile(db, current_user.id, profile_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    audit_logger.info("Profile updated", extra=extra_log)
    return updated_user

# =================================
# Security Information Routes
# =================================

@router.get("/security/summary", response_model=schemas.SecuritySummaryResponse)
async def get_security_summary(
    hours: int = 24,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get security event summary for the current user.
    """
    from ...audit_service import audit_service
    
    summary = await audit_service.get_security_summary(db, str(current_user.id), hours)
    return summary

@router.get("/audit-logs", response_model=schemas.AuditLogListResponse)
async def get_audit_logs(
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get audit logs for the current user.
    """
    from ...audit_service import audit_service
    
    logs = await audit_service.get_audit_logs(
        db, str(current_user.id), event_type, severity, None, None, limit, offset
    )
    
    return {
        "logs": logs,
        "total_count": len(logs)
    }
