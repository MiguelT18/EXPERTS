from enum import Enum

class MediaType(str, Enum):
	IMAGE = "IMAGE"
	VIDEO = "VIDEO"
	AUDIO = "AUDIO"
	DOCUMENT = "DOCUMENT"
	OTHER = "OTHER"

class BranchStatus(str, Enum):
	ACTIVE = "ACTIVE"
	INACTIVE = "INACTIVE"
	CLOSED = "CLOSED"
	MAINTENANCE = "MAINTENANCE"

class UserRole(str, Enum):
	USER = "USER"
	ADMIN = "ADMIN"
	OWNER = "OWNER"

class ResourceStatus(str, Enum):
	ACTIVE = "ACTIVE"
	INACTIVE = "INACTIVE"
	MAINTENANCE = "MAINTENANCE"
	LOST = "LOST"
	DISCARDED = "DISCARDED"

class ResourceTransferStatus(str, Enum):
	PENDING = "PENDING"
	SENT = "SENT"
	RECEIVED = "RECEIVED"
	CANCELLED = "CANCELLED"

class TokenType(str, Enum):
	RESET_PASSWORD = "RESET_PASSWORD"
	EMAIL_VERIFICATION = "EMAIL_VERIFICATION"

class UserStatus(str, Enum):
	ACTIVE = "ACTIVE"
	INACTIVE = "INACTIVE"

class ChatRoomType(str, Enum):
  PRIVATE = "PRIVATE"
  BRANCH = "BRANCH"
  INTER_BRANCH = "INTER_BRANCH"

class NotificationType(str, Enum):
  INVITATION = "INVITATION"
  ALERT = "ALERT"
  MESSAGE = "MESSAGE"
  SYSTEM = "SYSTEM"

class InvitationStatus(str, Enum):
  PENDING = "PENDING"
  ACCEPTED = "ACCEPTED"
  DECLINED = "DECLINED"
  EXPIRED = "EXPIRED"