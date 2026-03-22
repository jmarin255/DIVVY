import secrets
import string

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, text
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


def generate_join_code(length: int = 5) -> str:
	alphabet = string.ascii_letters + string.digits
	return "".join(secrets.choice(alphabet) for _ in range(length))


class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True, index=True)
	first_name = Column(String(100), nullable=False)
	last_name = Column(String(100), nullable=False)
	email = Column(String(255), nullable=False, unique=True)
	phone = Column(String(20), unique=True)
	password_hash = Column(Text, nullable=False)
	created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

	group_memberships = relationship("GroupMembership", back_populates="user", cascade="all, delete-orphan")
	refresh_sessions = relationship("RefreshSession", back_populates="user", cascade="all, delete-orphan")


class Group(Base):
	__tablename__ = "groups"

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String(255), nullable=False)
	join_code = Column(String(5), nullable=False, unique=True, default=generate_join_code)
	created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

	memberships = relationship("GroupMembership", back_populates="group", cascade="all, delete-orphan")


class GroupMembership(Base):
	__tablename__ = "group_memberships"
	__table_args__ = (
		CheckConstraint("role IN ('owner', 'member')", name="group_memberships_role_check"),
		UniqueConstraint("user_id", "group_id", name="unique_membership"),
		Index(
			"one_owner_per_group",
			"group_id",
			unique=True,
			postgresql_where=text("role = 'owner'"),
		),
	)

	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
	group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
	role = Column(String(20), nullable=False)
	joined_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

	user = relationship("User", back_populates="group_memberships")
	group = relationship("Group", back_populates="memberships")


class RefreshSession(Base):
	__tablename__ = "refresh_sessions"

	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
	token_hash = Column(String(64), nullable=False, unique=True, index=True)
	expires_at = Column(DateTime, nullable=False, index=True)
	revoked_at = Column(DateTime, nullable=True)
	created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

	user = relationship("User", back_populates="refresh_sessions")
