from uuid import UUID
from app.db.session import redis_client, engine
from app.schemas.models import User, Person
from sqlmodel import Session, select, delete
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone, timedelta
import logging
import functools

logger = logging.getLogger(__name__)

# Decorador para acceso seguro a atributos opcionales
def safe_field_access(func):
  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except (AttributeError, TypeError) as e:
      logger.error(f"[ERROR] Fallo de acceso seguro a campo: {e}")
      logger.error(f"[ERROR] Detalles completos: {str(e)}")
      logger.error(f"[ERROR] En la función: {func.__name__} con los argumentos: {args} {kwargs}")
      return None
  return wrapper

@safe_field_access
def get_user_age(user: User, now: datetime) -> timedelta:
  if not user.created_at:
    logger.warning(f"[WARNING] Usuario {user.id} no tiene created_at, omitiendo...")
    return None
  return now - user.created_at

def safe_delete(session: Session, model, condition):
  try:
    session.exec(delete(model).where(condition))
  except Exception as e:
    logger.warning(f"[WARNING] No se pudo eliminar en {model.__tablename__}: {e}", exc_info=True)

def clean_unverified_users():
  with Session(engine) as session:
    now = datetime.now(timezone.utc)

    stmt = select(User).where(User.is_verified == False).options(joinedload(User.person, innerjoin=False))
    unverified_users = session.exec(stmt).all()
    logger.info(f"[INFO] Total de usuarios no verificados: {len(unverified_users)}")

    if not unverified_users:
      logger.info("[INFO] No hay usuarios no verificados para limpiar.")
      return

    redis = redis_client
    verification_keys = redis.keys("verify_email:*")
    user_ids_with_active_codes = {
      UUID(redis.hget(key, "user_id").decode())
      for key in verification_keys
      if redis.hget(key, "user_id")
    }

    users_to_delete = []

    for user in unverified_users:
      if not isinstance(user, User):
        logger.error(f"[ERROR] Objeto no es instancia de User: {user}")
        continue

      if user.id in user_ids_with_active_codes:
        logger.info(f"[INFO] Usuario {user.email} tiene código de verificación activo, no eliminar.")
        continue

      user_age = get_user_age(user, now)
      if user_age and user_age > timedelta(hours=1):
        users_to_delete.append(user)

    user_ids = [user.id for user in users_to_delete]

    if not user_ids:
      logger.info("[INFO] No hay usuarios candidatos para eliminar.")
      return

    try:
      with session.begin():
        logger.info(f"[INFO] Eliminando usuarios: {user_ids}")

        safe_delete(session, Person, Person.user_id.in_(user_ids))
        safe_delete(session, User, User.id.in_(user_ids))

        logger.info(f"[INFO] Eliminados {len(user_ids)} usuarios no verificados exitosamente.")

    except Exception as e:
      logger.error(f"[ERROR] Fallo al eliminar usuarios: {e}", exc_info=True)
      session.rollback()