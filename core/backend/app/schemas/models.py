from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime
from uuid import uuid4, UUID
from .enum import *
from sqlalchemy import func

def utcnow_column():
  return Field(
    sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()),
    default_factory=lambda: datetime.now(timezone.utc)
  )

class User(SQLModel, table=True):
  id: UUID = Field(default_factory=uuid4, primary_key=True)
  username: str = Field(index=True)
  email: str = Field(index=True)
  role: UserRole = UserRole.USER
  password: str
  status: UserStatus = UserStatus.INACTIVE
  is_verified: bool = Field(default=False)
  created_at: datetime = utcnow_column()
  updated_at: datetime = utcnow_column()

  # relationships
  branches: List["Branch"] = Relationship(back_populates="user")
  business: List["Business"] = Relationship(back_populates="owner")
  person: "Person" = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False})
  rooms: List["ChatParticipant"] = Relationship(back_populates="user")
  messages: List["ChatMessage"] = Relationship(back_populates="sender")
  resources_created: List["Resource"] = Relationship(back_populates="user")
  transfer_records: List["ResourceTransferRecord"] = Relationship(back_populates="user")
  categories: List["Category"] = Relationship(back_populates="user")
  notifications_received: List["Notification"] = Relationship(
    back_populates="receiver",
    sa_relationship_kwargs={"foreign_keys": "[Notification.receiver_id]"}
  )
  notifications_sent: List["Notification"] = Relationship(
    back_populates="sender",
    sa_relationship_kwargs={"foreign_keys": "[Notification.sender_id]"}
  )
  invitations_received: List["Invitation"] = Relationship(
    back_populates="invited_user",
    sa_relationship_kwargs={"foreign_keys": "[Invitation.invited_user_id]"}
  )
  invitations_sent: List["Invitation"] = Relationship(
    back_populates="invited_by",
    sa_relationship_kwargs={"foreign_keys": "[Invitation.inviter_id]"}
  )

class Person(SQLModel, table=True):
  user_id: UUID = Field(foreign_key="user.id", primary_key=True)
  full_name: str
  picture: Optional[str] = None
  branch_id: Optional[UUID] = Field(foreign_key="branch.id", index=True)
  business_id: Optional[UUID] = Field(foreign_key="business.id", index=True)
  ci: Optional[int] = Field(default=None, index=True)
  phone_number: Optional[str] = Field(default=None, index=True)
  address: Optional[str] = None
  city: Optional[str] = None
  state: Optional[str] = None
  country: str = Field(default="Bolivia")
  birth_date: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))
  created_at: datetime = utcnow_column()
  updated_at: datetime = utcnow_column()

  # relationships
  user: "User" = Relationship(back_populates="person", sa_relationship_kwargs={"uselist": False})
  branch: "Branch" = Relationship(back_populates="people")
  business: "Business" = Relationship(back_populates="people")

class Business(SQLModel, table=True):
  id: UUID = Field(default_factory=uuid4, primary_key=True)
  name: str = Field(index=True)
  description: Optional[str] = None
  created_by: UUID = Field(foreign_key="user.id")
  created_at: datetime = utcnow_column()
  updated_at: datetime = utcnow_column()

  # relationships
  owner: "User" = Relationship(back_populates="business")
  branches: List["Branch"] = Relationship(back_populates="business")
  resources: List["Resource"] = Relationship(back_populates="business")
  categories: List["Category"] = Relationship(back_populates="business")
  people: List["Person"] = Relationship(back_populates="business")
  invitations: List["Invitation"] = Relationship(back_populates="business")
  notifications_sent: List["Notification"] = Relationship(
    back_populates="sender_business",
    sa_relationship_kwargs={"foreign_keys": "[Notification.business_id]"}
  )
  notifications_received: List["Notification"] = Relationship(
    back_populates="receiver_business",
    sa_relationship_kwargs={"foreign_keys": "[Notification.business_id]"}
  )
  rooms: List["ChatRoom"] = Relationship(back_populates="business")
  transfer_records_from: List["ResourceTransferRecord"] = Relationship(
    back_populates="from_business",
    sa_relationship_kwargs={"foreign_keys": "[ResourceTransferRecord.from_business_id]"}
  )
  transfer_records_to: List["ResourceTransferRecord"] = Relationship(
    back_populates="to_business",
    sa_relationship_kwargs={"foreign_keys": "[ResourceTransferRecord.to_business_id]"}
  )

class Resource(SQLModel, table=True):
  id: UUID = Field(default_factory=uuid4, primary_key=True)
  name: str = Field(index=True)
  description: Optional[str] = None
  price: float = Field(default=0)
  stock: int = Field(default=1)
  serial_number: str = Field(index=True)
  asset_number: Optional[str] = Field(index=True)
  status: ResourceStatus = Field(default=ResourceStatus.ACTIVE)
  location: Optional[str] = None
  tracking_qr_code: Optional[str] = None
  last_scanned_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
  category_id: UUID = Field(foreign_key="category.id")
  branch_id: UUID = Field(default=None, foreign_key="branch.id")
  business_id: UUID = Field(default=None, foreign_key="business.id")
  created_by: UUID = Field(foreign_key="user.id")
  created_at: datetime = utcnow_column()
  updated_at: datetime = utcnow_column()

  # relationships
  user: "User" = Relationship(back_populates="resources_created")
  media: List["ResourceMedia"] = Relationship(back_populates="resource")
  category: Optional["Category"] = Relationship(back_populates="resources")
  branch: Optional["Branch"] = Relationship(back_populates="resources")
  transfer_records: List["ResourceTransferRecord"] = Relationship(back_populates="resource")
  business: Optional["Business"] = Relationship(back_populates="resources")

class Branch(SQLModel, table=True):
  id: UUID = Field(default_factory=uuid4, primary_key=True)
  name: str = Field(index=True)
  business_id: UUID | None = Field(default=None, foreign_key="business.id", nullable=True)
  status: BranchStatus = Field(default=BranchStatus.ACTIVE)
  address: Optional[str] = None
  city: Optional[str] = None
  state: Optional[str] = None
  country: str = Field(default="Bolivia")
  created_by: UUID = Field(foreign_key="user.id")
  created_at: datetime = utcnow_column()
  updated_at: datetime = utcnow_column()

  # relationships
  user: "User" = Relationship(back_populates="branches")
  resources: List["Resource"] = Relationship(back_populates="branch")
  people: List["Person"] = Relationship(back_populates="branch")
  transfer_records_from: List["ResourceTransferRecord"] = Relationship(
    back_populates="from_branch",
    sa_relationship_kwargs={"foreign_keys": "[ResourceTransferRecord.from_branch_id]"}
  )
  transfer_records_to: List["ResourceTransferRecord"] = Relationship(
    back_populates="to_branch",
    sa_relationship_kwargs={"foreign_keys": "[ResourceTransferRecord.to_branch_id]"}
  )
  invitations: List["Invitation"] = Relationship(back_populates="branch")
  notifications_received: List["Notification"] = Relationship(
    back_populates="receiver_branch",
    sa_relationship_kwargs={"foreign_keys": "[Notification.branch_id]"}
  )
  notifications_sent: List["Notification"] = Relationship(
    back_populates="sender_branch",
    sa_relationship_kwargs={"foreign_keys": "[Notification.branch_id]"}
  )
  business: "Business" = Relationship(back_populates="branches")
  categories: List["Category"] = Relationship(back_populates="branch")
  rooms: List["ChatRoom"] = Relationship(back_populates="branch")

class ResourceMedia(SQLModel, table=True):
  id: UUID = Field(default_factory=uuid4, primary_key=True)
  url: str
  type: MediaType
  resource_id: UUID = Field(foreign_key="resource.id")
  created_at: datetime = utcnow_column()
  updated_at: datetime = utcnow_column()

  # relationships
  resource: "Resource" = Relationship(back_populates="media")

class ResourceTransferRecord(SQLModel, table=True):
  id: UUID = Field(default_factory=uuid4, primary_key=True)
  resource_id: UUID = Field(foreign_key="resource.id")
  from_branch_id: UUID = Field(foreign_key="branch.id")
  to_branch_id: UUID = Field(foreign_key="branch.id")
  from_business_id: Optional[UUID] = Field(foreign_key="business.id")
  to_business_id: Optional[UUID] = Field(foreign_key="business.id")
  status: ResourceTransferStatus = Field(default=ResourceTransferStatus.PENDING)
  initiated_by: UUID = Field(foreign_key="user.id")
  created_at: datetime = utcnow_column()
  updated_at: datetime = utcnow_column()

  resource: "Resource" = Relationship(back_populates="transfer_records")
  user: "User" = Relationship(back_populates="transfer_records")
  from_branch: "Branch" = Relationship(
    back_populates="transfer_records_from",
    sa_relationship_kwargs={"foreign_keys": "[ResourceTransferRecord.from_branch_id]"}
  )
  to_branch: "Branch" = Relationship(
    back_populates="transfer_records_to",
    sa_relationship_kwargs={"foreign_keys": "[ResourceTransferRecord.to_branch_id]"}
  )
  from_business: "Business" = Relationship(
    back_populates="transfer_records_from",
    sa_relationship_kwargs={"foreign_keys": "[ResourceTransferRecord.from_business_id]"}
  )
  to_business: "Business" = Relationship(
    back_populates="transfer_records_to",
    sa_relationship_kwargs={"foreign_keys": "[ResourceTransferRecord.to_business_id]"}
  )

class Category(SQLModel, table=True):
  id: UUID = Field(default_factory=uuid4, primary_key=True)
  name: str = Field(index=True)
  type: Optional[str] = None
  business_id: UUID = Field(foreign_key="business.id")
  branch_id: UUID = Field(foreign_key="branch.id")
  created_by: UUID = Field(foreign_key="user.id")
  created_at: datetime = utcnow_column()
  updated_at: datetime = utcnow_column()

  # relationships
  resources: List["Resource"] = Relationship(back_populates="category")
  user: "User" = Relationship(back_populates="categories")
  business: "Business" = Relationship(back_populates="categories")
  branch: "Branch" = Relationship(back_populates="categories")

class ChatMessage(SQLModel, table=True):
  id: UUID = Field(default_factory=uuid4, primary_key=True)
  room_id: UUID = Field(foreign_key="chatroom.id")
  sender_id: UUID = Field(foreign_key="user.id")
  content: str
  seen: bool = Field(default=False)
  sent_at: datetime = utcnow_column()
  updated_at: datetime = utcnow_column()

  # relationships
  room: "ChatRoom" = Relationship(back_populates="messages")
  sender: "User" = Relationship(back_populates="messages")

class ChatRoom(SQLModel, table=True):
  id: UUID = Field(default_factory=uuid4, primary_key=True)
  type: ChatRoomType
  title: str
  description: str
  business_id: UUID = Field(foreign_key="business.id")
  branch_id: UUID = Field(foreign_key="branch.id")
  created_at: datetime = utcnow_column()
  updated_at: datetime = utcnow_column()

  # relationships
  messages: List["ChatMessage"] = Relationship(back_populates="room")
  participants: List["ChatParticipant"] = Relationship(back_populates="room")
  business: "Business" = Relationship(back_populates="rooms")
  branch: "Branch" = Relationship(back_populates="rooms")

class ChatParticipant(SQLModel, table=True):
  id: UUID = Field(default_factory=uuid4, primary_key=True)
  room_id: UUID = Field(foreign_key="chatroom.id")
  user_id: UUID = Field(foreign_key="user.id")
  joined_at: datetime = utcnow_column()

  # relationships
  room: "ChatRoom" = Relationship(back_populates="participants")
  user: "User" = Relationship(back_populates="rooms")

class Notification(SQLModel, table=True):
  id: UUID = Field(default_factory=uuid4, primary_key=True)
  receiver_id: UUID = Field(foreign_key="user.id")
  sender_id: Optional[UUID] = Field(default=None, foreign_key="user.id")
  type: NotificationType
  target_id: Optional[UUID] = Field(default=None, index=True)
  title: str
  message: str
  url: Optional[str] = None
  is_read: bool = Field(default=False)
  business_id: Optional[UUID] = Field(default=None, foreign_key="business.id")
  branch_id: Optional[UUID] = Field(default=None, foreign_key="branch.id")
  created_at: datetime = utcnow_column()

  # relationships
  receiver: "User" = Relationship(
    back_populates="notifications_received",
    sa_relationship_kwargs={"foreign_keys": "[Notification.receiver_id]"}
  )
  sender: Optional["User"] = Relationship(
    back_populates="notifications_sent",
    sa_relationship_kwargs={"foreign_keys": "[Notification.sender_id]"}
  )
  sender_business: "Business" = Relationship(
    back_populates="notifications_sent",
    sa_relationship_kwargs={"foreign_keys": "[Notification.business_id]"}
  )
  sender_branch: "Branch" = Relationship(
    back_populates="notifications_sent",
    sa_relationship_kwargs={"foreign_keys": "[Notification.branch_id]"}
  )
  receiver_business: "Business" = Relationship(
    back_populates="notifications_received",
    sa_relationship_kwargs={"foreign_keys": "[Notification.business_id]"}
  )
  receiver_branch: "Branch" = Relationship(
    back_populates="notifications_received",
    sa_relationship_kwargs={"foreign_keys": "[Notification.branch_id]"}
  )
  business: Optional["Business"] = Relationship(back_populates="notifications_received")
  branch: Optional["Branch"] = Relationship(back_populates="notifications_received")

class Invitation(SQLModel, table=True):
  id: UUID = Field(default_factory=uuid4, primary_key=True)
  branch_id: UUID = Field(foreign_key="branch.id")
  business_id: UUID = Field(foreign_key="business.id")
  invited_user_email: str
  invited_user_id: Optional[UUID] = Field(default=None, foreign_key="user.id")
  inviter_id: UUID = Field(foreign_key="user.id")
  status: InvitationStatus = Field(default=InvitationStatus.PENDING)
  token: UUID = Field(default_factory=uuid4)
  expires_at: datetime
  created_at: datetime = utcnow_column()

  # relationships
  invited_by: "User" = Relationship(
    back_populates="invitations_sent",
    sa_relationship_kwargs={"foreign_keys": "[Invitation.inviter_id]"}
  )
  invited_user: Optional["User"] = Relationship(
    back_populates="invitations_received",
    sa_relationship_kwargs={"foreign_keys": "[Invitation.invited_user_id]"}
  )
  branch: "Branch" = Relationship(back_populates="invitations")
  business: "Business" = Relationship(back_populates="invitations")