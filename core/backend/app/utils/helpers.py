from email.message import EmailMessage
from fastapi import Header, HTTPException, status
from passlib.context import CryptContext
from app.config import settings
import aiosmtplib
import random

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_bearer_token(authorization: str = Header(...)) -> str:
  if not authorization.startswith("Bearer "):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Formato de autorización inválido.")
  return authorization.split(" ")[1]

def hash_password(password: str) -> str:
  return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
  return pwd_context.verify(password, hashed_password)

async def send_email(to, subject, body):
  if not to or not subject or not body:
    raise ValueError("Faltan campos obligatorios!")
  
  msg = EmailMessage()
  msg["From"] = settings.SMTP_USER
  msg["To"] = to
  msg["Subject"] = subject
  msg.set_content(body)
  
  try:
    await aiosmtplib.send(
      msg,
      hostname="smtp.gmail.com",
      port=465,
      username=settings.SMTP_USER,
      password=settings.SMTP_PASSWORD,
      use_tls=True
    )
  except Exception as e:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def generate_verification_code():
  return random.randint(100000, 999999)