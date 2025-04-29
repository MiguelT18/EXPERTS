from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from app.db.session import get_session
from app.utils.jwt import JWT
from app.utils.helpers import hash_password, send_email, generate_verification_code, verify_password
from app.schemas.schemas import UserCreate, UserLogin
from app.schemas.models import User, Person, UserStatus
from app.db.session import get_redis
from app.security.dependencies import get_current_admin
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from redis import Redis
from uuid import UUID
from datetime import datetime, timezone, timedelta

router = APIRouter()
jwt = JWT()

@router.get("/", response_model=list)
async def get_all_users(
  session: Session = Depends(get_session),
  _: User = Depends(get_current_admin)
):
  users = session.exec(select(User)).all()

  result = []
  for user in users:
    person = session.get(Person, user.id)
    result.append({
      "user_id": str(user.id),
      "full_name": person.full_name,
      "username": user.username,
      "email": user.email,
      "ci": person.ci,
      "role": user.role,
      "branch_id": person.branch_id,
      "status": user.status,
      "picture": person.picture,
      "country": person.country,
      "created_at": user.created_at,
      "updated_at": user.updated_at,
    })
  
  return result

@router.post("/sign-up", status_code=status.HTTP_201_CREATED)
async def sign_up(
  user: UserCreate,
  session: Session = Depends(get_session),
  redis: Redis = Depends(get_redis)
):
  # Verifica si ya existe el usuario
  existing_user = session.exec(select(User).where(User.email == user.email)).first()
  if existing_user:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El usuario ya existe.")
  
  # Hashea la contraseña
  hashed_pw = hash_password(user.password)

  try:    
    # Crea y guarda el nuev usuario
    new_user = User(username=user.username, email=user.email, password=hashed_pw)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Crea la persona asociada al usuario
    new_person = Person(user_id=str(new_user.id), full_name=user.full_name)
    session.add(new_person)
    session.commit()
    session.refresh(new_person)

    # Genera y guarda el token de verificación en Redis
    verification_code = generate_verification_code()
    expires_in = 3600 # 1 hora
    redis.hset(f"verify_email:{verification_code}", mapping={
      "user_id": str(new_user.id),
      "email": new_user.email,
      "verification_code": verification_code,
      "created_at": datetime.now(timezone.utc).isoformat()
    })
    redis.expire(f"verify_email:{verification_code}", expires_in)

    # Envía el correo de verificación
    await send_email(user.email, "Verificación de cuenta", f"Por favor, verifica tu cuenta con el código: {verification_code}")

    return {"message": "Usuario creado exitosamente. Por favor, verifica tu correo electrónico para activar tu cuenta.", "user_id": str(new_user.id)}

  except IntegrityError as e:
    session.rollback()
    if "unique constraint" in str(e.orig):
      raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="El correo electrónico ya está en uso."
      )
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=str(e)
    )
  
  except Exception as e:
    session.rollback()
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=str(e)
    )

@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(
  payload: dict,
  session: Session = Depends(get_session),
  redis: Redis = Depends(get_redis)
):
  token = payload.get("verification_code")
  if not token:
    raise HTTPException(
      status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
      detail="El código de verificación es requerido."
    )

  # Recupera los datos del hash en Redis
  user_id = redis.hget(f"verify_email:{token}", "user_id")
  email = redis.hget(f"verify_email:{token}", "email")
  verification_code = redis.hget(f"verify_email:{token}", "verification_code")
  created_at = redis.hget(f"verify_email:{token}", "created_at")

  # Si el hash no existe en Redis, ha expirado o es inválido
  if not all([user_id, email, verification_code, created_at]):
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Token de verificación expirado o inválido."
    )

  # Verifica la expiración del código
  ttl = redis.ttl(f"verify_email:{token}")
  if ttl == -2:  # El token ha expirado
    # Elimina el usuario y la persona asociada
    user = session.get(User, UUID(user_id))
    if user:
      session.delete(user)
      session.commit()
      
      # Borra la persona asociada, si existe
      person = session.exec(select(Person).where(Person.user_id == user.id)).first()
      if person:
        session.delete(person)
        session.commit()

      # Elimina el token de Redis
      redis.delete(f"verify_email:{token}")

      raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Token de verificación expirado. El usuario ha sido eliminado."
      )

  # Continúa con la verificación
  user = session.get(User, UUID(user_id))
  if not user:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Usuario no encontrado."
    )

  # Verifica que el código coincida con el esperado
  if verification_code != token:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="El código de verificación no coincide."
    )

  print(f"Token recibido: {token}")
  print(f"Verification code en Redis: {verification_code}")

  # Si está verificado y el token es válido
  user.is_verified = True
  user.updated_at = datetime.now(timezone.utc)
  session.commit()

  # Elimina el token de Redis tras la verificación exitosa
  redis.delete(f"verify_email:{token}")

  return {"message": "Cuenta verificada exitosamente."}

@router.post("/sign-in", status_code=status.HTTP_200_OK)
async def sign_in(
  user: UserLogin,
  response: Response,
  session: Session = Depends(get_session),
  redis: Redis = Depends(get_redis)
):
  db_user = session.exec(select(User).where(User.email == user.email)).first()
  if not db_user or not verify_password(user.password, db_user.password):
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Credenciales inválidas."
    )

  if not db_user.is_verified:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Cuenta no verificada. Por favor, verifica tu correo electrónico."
    )
  
  # Verificar si el usuario ya tiene un refresh token en Redis y eliminarlo si existe
  refresh_token_key = f"refresh_token:{db_user.id}"
  if redis.exists(refresh_token_key):
    redis.delete(refresh_token_key) # Eliminar el refresh token anterior
  
  access_token = jwt.create_access_token({"sub": str(db_user.id)})
  refresh_token = jwt.create_refresh_token({"sub": str(db_user.id)})
  jti = jwt.decode(refresh_token).get("jti")

  refresh_token_key = f"refresh_token:{db_user.id}"
  redis.hset(refresh_token_key, mapping={
    "user_id": str(db_user.id),
    "jti": jti,
    "refresh_token": refresh_token,
  })
  ttl_in_seconds = 7 * 24 * 60 * 60 # 7 días
  redis.expire(refresh_token_key, ttl_in_seconds)

  db_user.status = UserStatus.ACTIVE
  session.commit()

  # Establecer la cookie HttpOnly con el refresh token
  response.set_cookie(
    key="refresh_token",
    value=refresh_token,
    httponly=True,
    secure=False,
    samesite="strict",
    max_age=60 * 60 * 24 * 7,
    path="/api/v1/users/refresh-token"
  )

  return {
    "message": "Inicio de sesión exitoso.",
    "access_token": access_token,
    "token_type": "bearer"
  }

@router.post("/sign-out", status_code=status.HTTP_200_OK)
async def sign_out(
  payload: dict,
  session: Session = Depends(get_session),
  redis: Redis = Depends(get_redis)
):
  user_id = payload.get("user_id")
  if not user_id:
    raise HTTPException(
      status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
      detail="El ID del usuario es requerido."
    )

  db_user = session.get(User, UUID(user_id))
  if not db_user:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Usuario no encontrado."
    )

  if not redis.exists(f"refresh_token:{user_id}"):
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="La sesión ya ha sido cerrada."
    )

  redis.delete(f"refresh_token:{user_id}")
  db_user.status = UserStatus.INACTIVE
  session.commit()

  return {"message": "Sesión cerrada correctamente."}

@router.post("/refresh-token", status_code=status.HTTP_200_OK)
async def refresh_token(
  request: Request,
  response: Response,
  session: Session = Depends(get_session),
  redis: Redis = Depends(get_redis)
):
  refresh_token = request.cookies.get("refresh_token")
  if not refresh_token:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Token de actualización no encontrado en cookies."
    )

  try:
    payload = jwt.decode(refresh_token)
    user_id = payload.get("sub")
    jti = payload.get("jti")
  except Exception:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Token de actualización inválido o expirado."
    )

  try:
    user_id = UUID(user_id)
  except ValueError:
    raise HTTPException(
      status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
      detail="ID de usuario inválido."
    )

  db_user = session.get(User, user_id)
  if not db_user:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Usuario no encontrado."
    )

  refresh_token_key = f"refresh_token:{user_id}"
  if not redis.exists(refresh_token_key):
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Sesión inválida o expirada."
    )

  stored_token = redis.hget(refresh_token_key, "refresh_token")

  if stored_token != refresh_token:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Token de actualización no coincide."
    )

  new_access_token = jwt.create_access_token({"sub": str(user_id)})
  new_refresh_token = jwt.create_refresh_token({"sub": str(user_id)})
  new_jti = jwt.decode(new_refresh_token).get("jti")

  redis.hset(refresh_token_key, mapping={
    "user_id": str(user_id),
    "jti": new_jti,
    "refresh_token": new_refresh_token
  })
  redis.expire(refresh_token_key, timedelta(days=7))

  response.set_cookie(
    key="refresh_token",
    value=new_refresh_token,
    httponly=False,
    secure=False,
    samesite="strict",
    max_age=60 * 60 * 24 * 7,
    path="/api/v1/users/refresh-token"
  )

  return {
    "message": "Tokens generados exitosamente.",
    "access_token": new_access_token,
    "token_type": "bearer"
  }

@router.delete("/delete", status_code=status.HTTP_200_OK)
async def delete_user(
  payload: dict,
  session: Session = Depends(get_session),
  _: User = Depends(get_current_admin)
):
  user = session.get(User, UUID(payload.get("user_id")))
  if not user:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Usuario no encontrado."
    )

  person = session.exec(select(Person).where(Person.user_id == user.id)).first()
  if person:
    session.delete(person)
    session.commit()

  session.delete(user)
  session.commit()

  return {"message": "Usuario eliminado exitosamente."}