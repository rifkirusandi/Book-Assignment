"""FastAPI router for Book CRUD endpoints."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Book, Author, BookStatus
from schemas import (
    BookCreate,
    BookUpdate,
    BookPartialUpdate,
    BookResponse,
    BookListResponse,
    StatusEnum,
)

router = APIRouter(prefix="/books", tags=["books"])


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_or_create_author(db: Session, author_data) -> Author:
    """Find an existing author by name, or create a new one."""
    existing = (
        db.query(Author)
        .filter(
            Author.first_name == author_data.first_name,
            Author.last_name == author_data.last_name,
        )
        .first()
    )
    if existing:
        return existing
    new_author = Author(
        first_name=author_data.first_name,
        last_name=author_data.last_name,
        bio=author_data.bio,
    )
    db.add(new_author)
    db.flush()
    return new_author


def _map_status(schema_enum: StatusEnum) -> BookStatus:
    """Convert the Pydantic StatusEnum to the SQLAlchemy BookStatus enum."""
    return BookStatus[schema_enum.name]


def _book_to_response(book: Book) -> BookResponse:
    """Convert a SQLAlchemy Book instance to a BookResponse schema."""
    return BookResponse.model_validate(book)


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/", response_model=BookResponse, status_code=201,
             summary="Create a new book")
def create_book(payload: BookCreate, db: Session = Depends(get_db)):
    """Create a new book with an associated author."""
    author = _get_or_create_author(db, payload.author)

    book = Book(
        title=payload.title,
        price=payload.price,
        discount_price=payload.discount_price,
        status=_map_status(payload.status),
        author=author,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return _book_to_response(book)


@router.get("/", response_model=BookListResponse,
            summary="List books with pagination")
def list_books(
    limit: int = Query(default=10, ge=1, le=100, description="Max results per page"),
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db),
):
    """Return a paginated list of books."""
    total = db.query(Book).count()
    books = db.query(Book).offset(offset).limit(limit).all()
    return BookListResponse(
        total=total,
        limit=limit,
        offset=offset,
        books=[_book_to_response(b) for b in books],
    )


@router.get("/{book_id}", response_model=BookResponse,
            summary="Get a single book by ID")
def get_book(book_id: int, db: Session = Depends(get_db)):
    """Retrieve a book by its unique ID."""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    return _book_to_response(book)


@router.put("/{book_id}", response_model=BookResponse,
            summary="Full update of a book (PUT)")
def update_book(book_id: int, payload: BookUpdate, db: Session = Depends(get_db)):
    """Replace all mutable fields of a book."""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")

    author = _get_or_create_author(db, payload.author)

    book.title = payload.title
    book.price = payload.price
    book.discount_price = payload.discount_price
    book.status = _map_status(payload.status)
    book.author = author
    book.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(book)
    return _book_to_response(book)


@router.patch("/{book_id}", response_model=BookResponse,
              summary="Partial update of a book (PATCH)")
def partial_update_book(
    book_id: int, payload: BookPartialUpdate, db: Session = Depends(get_db)
):
    """Update only the fields that are explicitly provided in the request body."""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")

    update_data = payload.model_dump(exclude_unset=True)

    # Handle nested author update
    if "author" in update_data:
        author_data = update_data.pop("author")
        if author_data:
            # Update existing author fields
            if "first_name" in author_data and author_data["first_name"] is not None:
                book.author.first_name = author_data["first_name"]
            if "last_name" in author_data and author_data["last_name"] is not None:
                book.author.last_name = author_data["last_name"]
            if "bio" in author_data and author_data["bio"] is not None:
                book.author.bio = author_data["bio"]

    # Handle status enum conversion
    if "status" in update_data and update_data["status"] is not None:
        update_data["status"] = _map_status(update_data["status"])

    # Apply scalar field updates
    for field, value in update_data.items():
        if hasattr(book, field):
            setattr(book, field, value)

    book.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(book)
    return _book_to_response(book)


@router.delete("/{book_id}", status_code=204,
               summary="Delete a book")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """Permanently delete a book by ID."""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    db.delete(book)
    db.commit()
    return None
