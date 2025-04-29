from datetime import timedelta, datetime, timezone
from app.config import settings
from jose import jwt
from uuid import uuid4

class JWT:
  def __init__(self, secret: str = settings.SECRET_KEY, algorithm: str = settings.ALGORITHM):
    self.secret = secret
    self.algorithm = algorithm

  def encode(self, payload: dict) -> str:
    return jwt.encode(payload, self.secret, algorithm=self.algorithm)

  def decode(self, token: str) -> dict:
    return jwt.decode(token, self.secret, algorithms=[self.algorithm])
  
  def create_access_token(self, data: dict, expires_delta: timedelta = timedelta(minutes=15)):
    to_encode = data.copy()
    jti = str(uuid4())
    to_encode.update({"jti": jti})
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = self.encode(to_encode)
    return encoded_jwt

  def create_refresh_token(self, data: dict, expires_delta: timedelta = timedelta(days=7)):
    to_encode = data.copy()
    jti = str(uuid4())
    to_encode.update({"jti": jti})
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = self.encode(to_encode)
    return encoded_jwt
