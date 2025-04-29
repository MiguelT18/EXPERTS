import os
from dotenv import load_dotenv

class Settings:
  def __init__(self):
    load_dotenv()
    self.DATABASE_URL: str = os.getenv("DATABASE_URL")
    self.REDIS_URL: str = os.getenv("REDIS_URL")
    self.SECRET_KEY: str = os.getenv("SECRET_KEY")
    self.ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    self.SMTP_USER: str = os.getenv("SMTP_USER")
    self.SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")

settings = Settings()