from datetime import datetime
from uuid import UUID
from app.schemas.enum import BranchStatus
from sqlmodel import Field
from pydantic import EmailStr, BaseModel

class UserCreate(BaseModel):
  full_name: str
  username: str = Field(min_length=3, max_length=20)
  email: EmailStr
  password: str = Field(min_length=8)

class UserLogin(BaseModel):
  email: EmailStr
  password: str

class BranchBase(BaseModel):
  name: str = Field(min_length=3, description="Nombre de la sucursal")
  address: str = Field(None, description="Dirección de la sucursal")
  city: str = Field(None, description="Ciudad de la sucursal")
  state: str = Field(None, description="Estado de la sucursal")
  country: str = Field("Bolivia", description="País de la sucursal")

class BranchCreate(BranchBase):
  pass

class BranchRead(BranchBase):
  id: UUID
  status: BranchStatus
  created_by: UUID
  created_at: datetime
  updated_at: datetime