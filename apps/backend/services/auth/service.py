from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from . import models, schemas, security

async def get_user_by_email(db: AsyncSession, email: str):
    """
    Retrieves a user by their email address.
    """
    result = await db.execute(select(models.User).where(models.User.email == email))
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
        hashed_password=hashed_password,
        roles=user.roles
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def authenticate_user(db: AsyncSession, email: str, password: str):
    """
    Authenticates a user.
    - Fetches the user by email.
    - Verifies the provided password against the stored hash.
    - Returns the user object on success, None on failure.
    """
    user = await get_user_by_email(db, email=email)
    if not user:
        return None # User not found
    if not security.verify_password(password, user.hashed_password):
        return None # Incorrect password

    return user
