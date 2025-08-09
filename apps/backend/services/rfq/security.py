import os
from typing import Optional
from jose import JWTError, jwt
from dotenv import load_dotenv

load_dotenv()

# This MUST be the same secret key used by the auth service
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "a_very_secret_key_that_should_be_long_and_random")
ALGORITHM = "HS256"

def decode_token(token: str) -> Optional[dict]:
    """
    Decodes a JWT token. Returns the payload if valid, otherwise None.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
