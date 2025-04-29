from fastapi import FastAPI
from app.api.v1.endpoints.user import router as users_router
from app.api.v1.endpoints.branch import router as branches_router
from app.db.session import create_tables
from apscheduler.schedulers.background import BackgroundScheduler
from app.tasks import clean_unverified_users

def create_app():
  app = FastAPI(title="Experts API", version="0.1.0")
  create_tables()
  app.include_router(users_router, prefix="/api/v1/users", tags=["Usuarios"])
  app.include_router(branches_router, prefix="/api/v1/branches", tags=["Sedes"])

  scheduler = BackgroundScheduler()
  scheduler.add_job(clean_unverified_users, 'interval', minutes=1)
  scheduler.start()

  @app.get("/api/v1/health", tags=["Health"])
  async def health():
    return {"status": "ok"}

  return app