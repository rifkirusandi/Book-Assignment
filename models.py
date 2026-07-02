"""SQLAlchemy database models for Book and Author."""

import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class BookStatus(str, enum.Enum):
    """Enum representing the publication status of a book."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Author(Base):
    """Author database model."""

    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    bio = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    books = relationship("Book", back_populates="author", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Author(id={self.id}, name='{self.first_name} {self.last_name}')>"


class Book(Base):
    """Book database model."""

    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False, index=True)
    price = Column(Float, nullable=False)
    discount_price = Column(Float, nullable=True)
    status = Column(Enum(BookStatus), default=BookStatus.DRAFT, nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    author = relationship("Author", back_populates="books")

    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}')>"
