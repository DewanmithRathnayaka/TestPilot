"""
Project SQLAlchemy ORM Model
Maps to the 'projects' table in SQLite.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.db.session import Base


class Project(Base):
    """
    Project entity representing an uploaded or registered software project.
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

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status}')>"
