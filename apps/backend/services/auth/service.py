import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from . import models, schemas, security

async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID):
    """
    Retrieves a user by their UUID.
    """
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str):
    """
    Retrieves a user by their email address.
    """
    result = await db.execute(select(models.User).where(models.User.email == email))
    return result.scalars().first()

async def get_user_by_phone_number(db: AsyncSession, phone_number: str):
    """
    Retrieves a user by their phone number.
    """
    result = await db.execute(select(models.User).where(models.User.phone_number == phone_number))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    """
    Creates a new user, hashing their password before saving.
    """
    # Check if user already exists
    db_user = await get_user_by_email(db, email=user.email)
    if db_user:
        return None # Indicate that the user already exists

    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        phone_number=user.phone_number,
        hashed_password=hashed_password,
        roles=user.roles
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def authenticate_user(db: AsyncSession, username: str, password: str):
    """
    Authenticates a user by username (which can be email or phone number).
    - Fetches the user by email or phone.
    - Verifies the provided password against the stored hash.
    - Checks account lockout status.
    - Returns the user object on success, None on failure.
    """
    from .rate_limiter import RateLimiter
    from .audit_service import audit_service
    
    user = None
    if "@" in username:
        user = await get_user_by_email(db, email=username)
    else:
        user = await get_user_by_phone_number(db, phone_number=username)

    if not user:
        return None # User not found
    
    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        return None # Account is locked
    
    # Check Redis-based account lock
    is_locked, _ = await RateLimiter.is_account_locked(str(user.id))
    if is_locked:
        return None # Account is temporarily locked
    
    if not security.verify_password(password, user.hashed_password):
        # Increment failed login attempts
        user.failed_login_attempts += 1
        
        # Lock account if too many failed attempts
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=30)
            await RateLimiter.lock_account(str(user.id), 30)
        
        await db.commit()
        return None # Incorrect password
    
    # Reset failed login attempts on successful authentication
    if user.failed_login_attempts > 0:
        user.failed_login_attempts = 0
        user.locked_until = None
        await RateLimiter.clear_login_attempts(str(user.id))
    
    # Update last login time
    user.last_login_at = datetime.utcnow()
    await db.commit()

    return user

async def create_kyc_document(db: AsyncSession, user_id: uuid.UUID, doc_in: schemas.KYCDocumentCreate):
    """
    Creates a new KYC document record for a user.
    """
    # TODO: Add logic to prevent too many pending documents.
    db_doc = models.KYCDocument(
        user_id=user_id,
        document_type=doc_in.document_type,
        file_storage_key=doc_in.file_storage_key
    )
    db.add(db_doc)
    await db.commit()
    await db.refresh(db_doc)
    return db_doc

async def get_kyc_documents_by_user(db: AsyncSession, user_id: uuid.UUID):
    """
    Retrieves all KYC documents for a specific user.
    """
    result = await db.execute(select(models.KYCDocument).where(models.KYCDocument.user_id == user_id))
    return result.scalars().all()

async def set_user_tfa_secret(db: AsyncSession, user_id: int, secret: str | None):
    """
    Set the TFA secret for a user.
    """
    user = await db.get(models.User, user_id)
    if user:
        user.tfa_secret = secret
        await db.commit()
    return user

async def set_user_tfa_enabled(db: AsyncSession, user_id: int, enabled: bool):
    """
    Enable or disable TFA for a user.
    """
    user = await db.get(models.User, user_id)
    if user:
        user.is_tfa_enabled = enabled
        await db.commit()
    return user

async def revoke_all_user_tokens(db: AsyncSession, user_id: uuid.UUID):
    """
    Revoke all tokens for a user by setting the tokens_revoked_at timestamp.
    """
    user = await get_user_by_id(db, user_id)
    if user:
        user.tokens_revoked_at = datetime.utcnow()
        await db.commit()
    return user

async def change_password(db: AsyncSession, user_id: uuid.UUID, current_password: str, new_password: str):
    """
    Change user password after verifying current password
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        return None
    
    # Verify current password
    if not security.verify_password(current_password, user.hashed_password):
        return None
    
    # Update password
    user.hashed_password = security.get_password_hash(new_password)
    user.password_changed_at = datetime.utcnow()
    
    # Revoke all existing tokens to force re-login
    user.tokens_revoked_at = datetime.utcnow()
    
    await db.commit()
    return user

async def generate_backup_codes(db: AsyncSession, user_id: uuid.UUID):
    """
    Generate new backup codes for user
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        return None
    
    backup_codes = security.generate_backup_codes()
    user.backup_codes = backup_codes
    await db.commit()
    
    return backup_codes

async def verify_backup_code(db: AsyncSession, user_id: uuid.UUID, backup_code: str):
    """
    Verify and consume a backup code
    """
    user = await get_user_by_id(db, user_id)
    if not user or not user.backup_codes:
        return False
    
    is_valid, remaining_codes = security.verify_backup_code(user.backup_codes, backup_code)
    
    if is_valid:
        user.backup_codes = remaining_codes
        await db.commit()
    
    return is_valid

async def unlock_user_account(db: AsyncSession, user_id: uuid.UUID):
    """
    Unlock user account (admin function)
    """
    from .rate_limiter import RateLimiter
    
    user = await get_user_by_id(db, user_id)
    if not user:
        return None
    
    # Reset database fields
    user.failed_login_attempts = 0
    user.locked_until = None
    
    # Clear Redis locks
    await RateLimiter.unlock_account(str(user_id))
    await RateLimiter.clear_login_attempts(str(user_id))
    
    await db.commit()
    return user

async def update_user_profile(db: AsyncSession, user_id: uuid.UUID, profile_data: dict):
    """
    Update user profile information
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        return None
    
    # Update allowed fields
    allowed_fields = ['first_name', 'last_name', 'timezone', 'language', 'phone_number']
    
    for field, value in profile_data.items():
        if field in allowed_fields and hasattr(user, field):
            setattr(user, field, value)
    
    await db.commit()
    return user
