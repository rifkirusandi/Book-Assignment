# Book CRUD API

A production-ready RESTful CRUD API for managing books, built with **FastAPI**, **SQLAlchemy**, and **SQLite**.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Database Choice: Why SQLite?](#database-choice-why-sqlite)
- [Pydantic Reflection](#pydantic-reflection)

---

## Features

- Full CRUD lifecycle for Books (Create, Read, Update, Delete)
- Nested Author model with relationship management
- Pydantic v2 validation with custom cross-field validators
- Computed fields (e.g., `net_price`)
- Enum-based status management (draft / published / archived)
- Pagination support (limit/offset) on list endpoints
- Full (PUT) and partial (PATCH) update support
- CORS middleware
- Interactive API docs via Swagger UI and ReDoc

## Tech Stack

| Component      | Technology                        |
| -------------- | --------------------------------- |
| Framework      | FastAPI                           |
| ORM            | SQLAlchemy 2.x                    |
| Validation     | Pydantic v2 + pydantic-settings   |
| Database       | SQLite (via `sqlite3`)            |
| Server         | Uvicorn (ASGI)                    |
| Testing        | FastAPI `TestClient` + `httpx`    |

## Project Structure

```
Book Assignment/
├── main.py              # App initialization, middleware, lifespan events
├── config.py            # Centralized settings via pydantic-settings
├── database.py          # SQLAlchemy engine, session factory, and dependency
├── models.py            # SQLAlchemy ORM models (Book, Author, BookStatus)
├── schemas.py           # Pydantic schemas (Create, Update, Response, etc.)
├── routers/
│   ├── __init__.py
│   └── books.py         # All book CRUD endpoints
├── requirements.txt     # Python dependencies
├── test_app.py          # Automated integration tests
└── README.md            # This file
```

## Setup & Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Steps

```bash
# 1. Navigate to the project directory
cd "Book Assignment"

# 2. Create and activate a virtual environment (recommended)
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Running the Application

```bash
# Start the development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Once running, access:
- **API Root**: [http://localhost:8000/](http://localhost:8000/)
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## API Endpoints

| Method   | Endpoint                  | Description                       |
| -------- | ------------------------- | --------------------------------- |
| `GET`    | `/`                       | Health check                      |
| `POST`   | `/api/v1/books/`          | Create a new book                 |
| `GET`    | `/api/v1/books/`          | List books (paginated)            |
| `GET`    | `/api/v1/books/{book_id}` | Get a single book by ID           |
| `PUT`    | `/api/v1/books/{book_id}` | Full update of a book             |
| `PATCH`  | `/api/v1/books/{book_id}` | Partial update of a book          |
| `DELETE` | `/api/v1/books/{book_id}` | Delete a book                     |

### Example Request — Create a Book

```json
POST /api/v1/books/
{
    "title": "The Pragmatic Programmer",
    "price": 49.99,
    "discount_price": 34.99,
    "status": "published",
    "author": {
        "first_name": "David",
        "last_name": "Thomas",
        "bio": "Co-author of The Pragmatic Programmer"
    }
}
```

### Example Response

```json
{
    "id": 1,
    "title": "The Pragmatic Programmer",
    "price": 49.99,
    "discount_price": 34.99,
    "status": "published",
    "author": {
        "id": 1,
        "first_name": "David",
        "last_name": "Thomas",
        "bio": "Co-author of The Pragmatic Programmer"
    },
    "created_at": "2025-01-15T10:30:00",
    "updated_at": "2025-01-15T10:30:00",
    "net_price": 34.99
}
```

---

## Database Choice: Why SQLite?

SQLite was chosen as the database for this project for several compelling reasons:

1. **Zero Configuration**: SQLite requires no server process, no configuration files, and no database administration. The entire database is a single file on disk, making setup instantaneous.

2. **Perfect for Assignments**: Since this is a demonstrative CRUD API, SQLite eliminates external dependencies (no need to install PostgreSQL or MongoDB), allowing the reviewer to clone the repo and run the app immediately.

3. **Full SQL Support**: Despite its simplicity, SQLite supports the full SQL standard, foreign keys, transactions, and all the relational features needed for a proper CRUD implementation.

4. **Seamless SQLAlchemy Integration**: SQLAlchemy abstracts the database layer, so migrating to PostgreSQL or MySQL in production would require only changing the `DATABASE_URL` connection string — no code changes needed.

5. **Portability**: The database file travels with the project, making it easy to share, test, and demonstrate without infrastructure setup.

For a production system with high concurrency requirements, PostgreSQL would be more appropriate. But for this assignment's scope, SQLite provides the best balance of simplicity and functionality.

---

## Pydantic Reflection

### What Was Tricky About Pydantic and How I Solved It

**1. Cross-Field Validation with `@model_validator`**

The requirement that `discount_price` must be strictly less than `price` is a cross-field constraint — it involves comparing two fields against each other. A simple `@field_validator` only has access to one field at a time, so it cannot perform this comparison.

**Solution**: I used Pydantic v2's `@model_validator(mode="after")`, which runs after all individual field validations pass and gives access to the entire model instance via `self`. This lets me compare `self.discount_price` against `self.price` and raise a `ValueError` with a clear message if the constraint is violated.

**2. Separate Schemas for Different Operations**

Reusing a single schema for create, update, and response operations quickly leads to problems: response models need fields like `id` and timestamps that shouldn't be in create requests, while update schemas need all fields to be optional for PATCH operations.

**Solution**: I created a clear schema hierarchy:
- `BookBase` — shared validated fields
- `BookCreate` / `BookUpdate` — extends base with required author (for POST and PUT)
- `BookPartialUpdate` — all fields optional with its own cross-field validator (for PATCH)
- `BookResponse` — adds `id`, timestamps, author response, and `@computed_field` for `net_price`

**3. The `@computed_field` Decorator**

Pydantic v2 introduced `@computed_field` as a way to add derived properties to models that are included in serialization. I used it to calculate `net_price` — the effective price the customer pays after applying any discount. This is not stored in the database but computed dynamically during response serialization.

**4. Handling `exclude_unset` for PATCH**

The PATCH endpoint uses `model_dump(exclude_unset=True)` to only extract fields explicitly sent in the request body. This is critical for partial updates — it distinguishes between "field was not provided" and "field was explicitly set to null", allowing us to update only the specified fields without overwriting others.

**5. Nested Model Serialization with `from_attributes`**

Since SQLAlchemy models are not dicts, Pydantic needs to know how to read their attributes. The `model_config = {"from_attributes": True}` setting tells Pydantic to read data from object attributes (like ORM instances) rather than expecting dict-like access, enabling seamless conversion from SQLAlchemy models to Pydantic response schemas.

---

## Running Tests

```bash
python test_app.py
```

## License

This project is created for educational/assignment purposes.
