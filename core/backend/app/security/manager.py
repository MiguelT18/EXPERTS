from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from redis import Redis
from app.config import settings
from app.db.session import get_redis

class SecurityManager():
  def __init__(self, redis: Redis = Depends(get_redis)):
    self.redis = redis
    self.secret = settings.SECRET_KEY
    self.algorithm = settings.ALGORITHM
  
  def verify_access_token(self, token: str) -> dict:
    try:
      payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
      return payload
    except JWTError:
      raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Tóken de acceso inválido o expirado.")

  def verify_refresh_token(self, refresh_token: str) -> dict:
    try:
      payload = jwt.decode(refresh_token, self.secret, algorithms=[self.algorithm])
      jti = payload.get("jti")
      stored = self.redis.get(f"refresh_token:{jti}")

      if not stored or stored.decode() != refresh_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Tóken de refresco inválido o expirado.")

      return payload
    except JWTError:
      raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Tóken de refresco inválido o expirado.")

