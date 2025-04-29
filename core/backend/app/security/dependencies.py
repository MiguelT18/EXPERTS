from fastapi import Request, HTTPException, Depends, status
from app.db.session import get_session
from app.utils.jwt import JWT
from sqlmodel import Session
from app.schemas.models import User
from app.schemas.enum import UserRole

jwt = JWT()

def get_current_admin(
  request: Request,
  session: Session = Depends(get_session)
) -> User:
  auth_header = request.headers.get("Authorization")
  if not auth_header or not auth_header.startswith("Bearer "):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tóken de acceso no proporcionado.")
  
  token = auth_header.split(" ")[1]
  try:
    payload = jwt.decode(token)
    user_id = payload.get("sub")
  except Exception:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tóken de acceso inválido o expirado.")
  
  user = session.get(User, user_id)
  if not user or user.role != UserRole.ADMIN:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado: se requiere rol ADMIN.")
  
  return user