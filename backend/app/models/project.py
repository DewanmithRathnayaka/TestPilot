"""
Project SQLAlchemy ORM Model
Maps to the 'projects' table in SQLite.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class Project(Base):
    """
    Project entity representing an uploaded or registered software project.
    Each project is linked to an owning User via user_id foreign key.
    """
    __tablename__ = "projects"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        doc="Unique primary key identifier for the project"
    )
    name = Column(
        String(100),
        nullable=False,
        index=True,
        doc="Name of the software project"
    )
    description = Column(
        Text,
        nullable=True,
        doc="Detailed explanation of the project functionality"
    )
    language = Column(
        String(50),
        nullable=False,
        default="Python",
        doc="Programming language of the project (default: Python)"
    )
    status = Column(
        String(50),
        nullable=False,
        default="Uploaded",
        doc="Current pipeline status of the project (e.g. Uploaded, Validated, Tested)"
    )
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Timestamp when the project record was inserted"
    )

    # Foreign Key: References the 'id' column of the 'users' table
    # nullable=True ensures backwards compatibility with existing Day 4 database records
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        doc="Foreign key linking the project to the owner user"
    )

    # Many-to-One Relationship: Each project belongs to one owning User
    owner = relationship("User", back_populates="projects")

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status}', user_id={self.user_id})>"
