from sqlmodel import Session, create_engine, SQLModel
from app.config import settings
from redis import Redis

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

def get_session():
  with Session(engine) as session:
    return session

redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)

def get_redis():
  return redis_client

def create_tables():
  SQLModel.metadata.create_all(engine)