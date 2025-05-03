from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session
from uuid import uuid4
from app.schemas.models import Branch, User
from app.schemas.enum import BranchStatus
from app.schemas.schemas import BranchCreate
from app.db.session import get_session
from app.security.dependencies import get_current_admin
from sqlmodel import select
from datetime import datetime, timezone

router = APIRouter()

@router.get("/", response_model=list)
async def get_all_branches(
  session: Session = Depends(get_session),
  _: User = Depends(get_current_admin)
):
  branches = session.exec(select(Branch)).all()

  result = []
  for branch in branches:
    result.append({
      "id": str(branch.id),
      "name": branch.name,
      "address": branch.address,
      "city": branch.city,
      "state": branch.state,
      "country": branch.country,
      "status": branch.status,
      "created_at": branch.created_at,
      "updated_at": branch.updated_at,
    })

  return result

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

@router.get("/{branch_id}", response_model=Branch)
async def get_branch_by_id(
  branch_id: str,
  session: Session = Depends(get_session),
  _: User = Depends(get_current_admin)
):
  branch = session.get(Branch, branch_id)
  if not branch:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Branch not found"
    )
  return branch

@router.put("/update/{branch_id}", status_code=status.HTTP_200_OK)
async def update_branch(
  branch_id: str,
  branch_data: BranchCreate,
  session: Session = Depends(get_session),
  _: User = Depends(get_current_admin)
):
  branch = session.get(Branch, branch_id)
  if not branch:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Branch not found"
    )

  if not branch_data:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Algunos campos son obligatorios."
    )

  if branch_data.name:
    branch.name = branch_data.name
  if branch_data.address:
    branch.address = branch_data.address
  if branch_data.city:
    branch.city = branch_data.city
  if branch_data.state:
    branch.state = branch_data.state
  if branch_data.country:
    branch.country = branch_data.country

  branch.updated_at = datetime.now(timezone.utc)

  session.add(branch)
  session.commit()
  session.refresh(branch)

  return branch
