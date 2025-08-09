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
    - Returns the user object on success, None on failure.
    """
    user = None
    if "@" in username:
        user = await get_user_by_email(db, email=username)
    else:
        user = await get_user_by_phone_number(db, phone_number=username)

    if not user:
        return None # User not found
    if not security.verify_password(password, user.hashed_password):
        return None # Incorrect password

    return user

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

async def revoke_all_user_tokens(db: AsyncSession, user_id: int):
    """
    Revoke all tokens for a user by setting the tokens_revoked_at timestamp.
    """
    user = await db.get(models.User, user_id)
    if user:
        user.tokens_revoked_at = datetime.utcnow()
        await db.commit()
    return user
