from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:
    return pwd_context.hash(p)

def verify_password(p: str, h: str) -> bool:
    return pwd_context.verify(p, h)

def create_access_token(subject: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_MINUTES)
    return jwt.encode({"sub": subject, "exp": exp, "type": "access"}, settings.JWT_SECRET, algorithm="HS256")

def create_refresh_token(subject: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_DAYS)
    return jwt.encode({"sub": subject, "exp": exp, "type": "refresh"}, settings.JWT_REFRESH_SECRET, algorithm="HS256")

def decode_token(token: str, refresh: bool = False) -> Optional[str]:
    secret = settings.JWT_REFRESH_SECRET if refresh else settings.JWT_SECRET
    ttype = "refresh" if refresh else "access"
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        if payload.get("type") != ttype:
            return None
        return payload.get("sub")
    except JWTError:
        return None