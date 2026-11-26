"""
User SQLAlchemy ORM Model
Maps to the 'users' table in SQLite.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.db.session import Base


class User(Base):
    """
    User entity representing a registered student or evaluator.
    """
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        doc="Unique primary key identifier for the user"
    )
    username = Column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
        doc="Unique username used for login and display"
    )
    email = Column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
        doc="Unique email address of the user"
    )
    hashed_password = Column(
        String(255),
        nullable=False,
        doc="Argon2id cryptographic hash of the user password"
    )
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Timestamp when the account was registered"
    )

    # One-to-Many Relationship: One user can own multiple projects
    projects = relationship(
        "Project",
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
