"""Pydantic schemas for request/response validation."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator, computed_field


# ── Enums ────────────────────────────────────────────────────────────────────

class StatusEnum(str, Enum):
    """Publication status options for a Book."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


# ── Author Schemas ───────────────────────────────────────────────────────────

class AuthorBase(BaseModel):
    """Base author fields."""
    first_name: str = Field(..., min_length=1, max_length=100, description="Author first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Author last name")
    bio: Optional[str] = Field(None, max_length=500, description="Short author biography")


class AuthorCreate(AuthorBase):
    """Schema for creating an author."""
    pass


class AuthorUpdate(BaseModel):
    """Schema for partially updating an author."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)


class AuthorResponse(AuthorBase):
    """Schema for returning an author in API responses."""
    id: int

    model_config = {"from_attributes": True}


# ── Book Schemas ─────────────────────────────────────────────────────────────

class BookBase(BaseModel):
    """Shared base fields for Book schemas."""
    title: str = Field(..., min_length=1, max_length=200, description="Book title (required)")
    price: float = Field(..., gt=0, description="Book price, must be positive")
    discount_price: Optional[float] = Field(
        None, ge=0, description="Optional discounted price"
    )
    status: StatusEnum = Field(
        default=StatusEnum.DRAFT, description="Publication status"
    )

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title must not be blank")
        return v.strip()

    @model_validator(mode="after")
    def validate_discount_less_than_price(self):
        """Custom cross-field validator: discount_price must be strictly less than price."""
        if self.discount_price is not None and self.discount_price >= self.price:
            raise ValueError(
                f"discount_price ({self.discount_price}) must be less than price ({self.price})"
            )
        return self


class BookCreate(BookBase):
    """Schema for creating a new book."""
    author: AuthorCreate


class BookUpdate(BookBase):
    """Schema for a full (PUT) update of a book."""
    author: AuthorCreate


class BookPartialUpdate(BaseModel):
    """Schema for a partial (PATCH) update of a book.
    All fields are optional; only supplied fields are updated.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    price: Optional[float] = Field(None, gt=0)
    discount_price: Optional[float] = Field(None, ge=0)
    status: Optional[StatusEnum] = None
    author: Optional[AuthorUpdate] = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Title must not be blank")
        return v.strip() if v else v

    @model_validator(mode="after")
    def validate_discount_less_than_price(self):
        if (
            self.discount_price is not None
            and self.price is not None
            and self.discount_price >= self.price
        ):
            raise ValueError(
                f"discount_price ({self.discount_price}) must be less than price ({self.price})"
            )
        return self


class BookResponse(BookBase):
    """Schema returned in API responses."""
    id: int
    author: AuthorResponse
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def net_price(self) -> float:
        """Calculated field: effective price after applying the discount.
        If a discount_price is set, net_price = discount_price; otherwise net_price = price.
        """
        if self.discount_price is not None:
            return self.discount_price
        return self.price

    model_config = {"from_attributes": True}


class BookListResponse(BaseModel):
    """Paginated list of books."""
    total: int
    limit: int
    offset: int
    books: list[BookResponse]
