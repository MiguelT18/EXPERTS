from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session
from uuid import uuid4
from app.schemas.models import Branch, User
from app.schemas.enum import BranchStatus
from app.schemas.schemas import BranchCreate
from app.db.session import get_session
from app.security.dependencies import get_current_admin

router = APIRouter()

@router.get("/", response_model=list)
async def get_all_branches():
  return ["branch1", "branch2", "branch3"]

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_branch(
  branch_data: BranchCreate,
  session: Session = Depends(get_session),
  admin_user: User = Depends(get_current_admin)
):
  if not all([branch_data.name, branch_data.address, branch_data.city, branch_data.state]):
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Algunos campos son obligatorios."
    )

  new_branch = Branch(
    id=uuid4(),
    name=branch_data.name,
    address=branch_data.address,
    city=branch_data.city,
    state=branch_data.state,
    status=BranchStatus.ACTIVE,
    country=branch_data.country or "Bolivia",
    updated_by=admin_user.id,
    created_by=admin_user.id,
  )

  session.add(new_branch)
  session.commit()
  session.refresh(new_branch)

  return {"message": "Branch created successfully"}