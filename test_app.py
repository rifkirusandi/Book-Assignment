"""Automated integration tests for the Book CRUD API.
Uses FastAPI's TestClient so no running server is needed."""

import sys
import os

# Ensure the project root is on the import path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient

from main import app
from database import engine, Base

# ── Setup: create a fresh test database ──────────────────────────────────────
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)

PASS = "✓"
FAIL = "✗"
results = []


def report(name: str, ok: bool, detail: str = ""):
    status = PASS if ok else FAIL
    results.append((name, ok))
    print(f"  {status}  {name}")
    if detail:
        print(f"      → {detail}")


# ═════════════════════════════════════════════════════════════════════════════
# TEST 1: Create a valid book and verify computed field
# ═════════════════════════════════════════════════════════════════════════════
print("\n═══ TEST 1: Create a valid book (with discount) ═══")

payload = {
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

resp = client.post("/api/v1/books/", json=payload)
print(f"  Status: {resp.status_code}")

if resp.status_code == 201:
    data = resp.json()
    report("HTTP 201 Created", True)
    report("Title matches", data["title"] == "The Pragmatic Programmer", data["title"])
    report("Price is correct", data["price"] == 49.99, str(data["price"]))
    report("Discount price is correct", data["discount_price"] == 34.99, str(data["discount_price"]))
    report("Status is 'published'", data["status"] == "published", data["status"])
    report("Author nested correctly", data["author"]["first_name"] == "David", str(data["author"]))
    report("Computed net_price == discount_price (34.99)", data.get("net_price") == 34.99,
           f"net_price={data.get('net_price')}")
    report("ID assigned", data["id"] == 1, f"id={data.get('id')}")
    report("Timestamps present", "created_at" in data and "updated_at" in data)
else:
    report("HTTP 201 Created", False, f"Got {resp.status_code}: {resp.text}")

# ── Create a second book (no discount) to verify net_price == price ──────────
print("\n═══ TEST 1b: Create book without discount ═══")

payload2 = {
    "title": "Clean Code",
    "price": 39.99,
    "status": "draft",
    "author": {
        "first_name": "Robert",
        "last_name": "Martin"
    }
}

resp2 = client.post("/api/v1/books/", json=payload2)
print(f"  Status: {resp2.status_code}")

if resp2.status_code == 201:
    data2 = resp2.json()
    report("HTTP 201 Created (no discount)", True)
    report("discount_price is null", data2["discount_price"] is None, str(data2["discount_price"]))
    report("Computed net_price == price (39.99)", data2.get("net_price") == 39.99,
           f"net_price={data2.get('net_price')}")
else:
    report("HTTP 201 Created (no discount)", False, f"Got {resp2.status_code}: {resp2.text}")


# ═════════════════════════════════════════════════════════════════════════════
# TEST 2: Attempt to create an invalid book (discount_price > price)
# ═════════════════════════════════════════════════════════════════════════════
print("\n═══ TEST 2: Invalid book — discount_price > price ═══")

bad_payload = {
    "title": "Bad Book",
    "price": 10.00,
    "discount_price": 15.00,
    "status": "draft",
    "author": {
        "first_name": "Bad",
        "last_name": "Author"
    }
}

resp = client.post("/api/v1/books/", json=bad_payload)
print(f"  Status: {resp.status_code}")

report("HTTP 422 Validation Error", resp.status_code == 422,
       f"Got {resp.status_code}")
if resp.status_code == 422:
    error_body = resp.json()
    report("Error detail returned", "detail" in error_body,
           str(error_body.get("detail", ""))[:120])


# ═════════════════════════════════════════════════════════════════════════════
# TEST 2b: Additional validation — negative price
# ═════════════════════════════════════════════════════════════════════════════
print("\n═══ TEST 2b: Invalid book — negative price ═══")

bad_payload2 = {
    "title": "Negative Price Book",
    "price": -5.00,
    "status": "draft",
    "author": {"first_name": "A", "last_name": "B"}
}

resp = client.post("/api/v1/books/", json=bad_payload2)
print(f"  Status: {resp.status_code}")
report("HTTP 422 for negative price", resp.status_code == 422, f"Got {resp.status_code}")


# ═════════════════════════════════════════════════════════════════════════════
# TEST 3: List books with pagination
# ═════════════════════════════════════════════════════════════════════════════
print("\n═══ TEST 3: List books with pagination ═══")

resp = client.get("/api/v1/books/")
print(f"  Status: {resp.status_code}")

if resp.status_code == 200:
    data = resp.json()
    report("HTTP 200 OK", True)
    report("Total count is 2", data["total"] == 2, f"total={data['total']}")
    report("Default limit applied", data["limit"] == 10, f"limit={data['limit']}")
    report("Default offset is 0", data["offset"] == 0, f"offset={data['offset']}")
    report("Books list has 2 items", len(data["books"]) == 2, f"len={len(data['books'])}")
else:
    report("HTTP 200 OK", False, f"Got {resp.status_code}: {resp.text}")

# ── Pagination: limit=1 ──────────────────────────────────────────────────────
print("\n═══ TEST 3b: Pagination with limit=1 ═══")

resp = client.get("/api/v1/books/", params={"limit": 1, "offset": 0})
print(f"  Status: {resp.status_code}")

if resp.status_code == 200:
    data = resp.json()
    report("Returns 1 book per page", len(data["books"]) == 1, f"len={len(data['books'])}")
    report("Total still reflects all books", data["total"] == 2, f"total={data['total']}")
    report("Limit in response is 1", data["limit"] == 1, f"limit={data['limit']}")
else:
    report("Pagination limit=1", False, f"Got {resp.status_code}")

# ── Pagination: offset=1 ─────────────────────────────────────────────────────
print("\n═══ TEST 3c: Pagination with offset=1 ═══")

resp = client.get("/api/v1/books/", params={"limit": 1, "offset": 1})
print(f"  Status: {resp.status_code}")

if resp.status_code == 200:
    data = resp.json()
    report("Returns 1 book at offset 1", len(data["books"]) == 1, f"len={len(data['books'])}")
    report("Offset in response is 1", data["offset"] == 1, f"offset={data['offset']}")
else:
    report("Pagination offset=1", False, f"Got {resp.status_code}")


# ═════════════════════════════════════════════════════════════════════════════
# TEST 4: GET single book by ID
# ═════════════════════════════════════════════════════════════════════════════
print("\n═══ TEST 4: Get single book by ID ═══")

resp = client.get("/api/v1/books/1")
print(f"  Status: {resp.status_code}")

if resp.status_code == 200:
    data = resp.json()
    report("HTTP 200 OK", True)
    report("Correct book returned", data["title"] == "The Pragmatic Programmer", data["title"])
else:
    report("GET by ID", False, f"Got {resp.status_code}")

# ── 404 for non-existent book ────────────────────────────────────────────────
resp_404 = client.get("/api/v1/books/999")
report("404 for non-existent book", resp_404.status_code == 404, f"Got {resp_404.status_code}")


# ═════════════════════════════════════════════════════════════════════════════
# TEST 5: PUT (full update)
# ═════════════════════════════════════════════════════════════════════════════
print("\n═══ TEST 5: PUT full update ═══")

put_payload = {
    "title": "The Pragmatic Programmer (2nd Ed)",
    "price": 59.99,
    "discount_price": 44.99,
    "status": "published",
    "author": {
        "first_name": "David",
        "last_name": "Thomas",
        "bio": "Updated bio"
    }
}

resp = client.put("/api/v1/books/1", json=put_payload)
print(f"  Status: {resp.status_code}")

if resp.status_code == 200:
    data = resp.json()
    report("HTTP 200 OK", True)
    report("Title updated", data["title"] == "The Pragmatic Programmer (2nd Ed)", data["title"])
    report("Price updated", data["price"] == 59.99, str(data["price"]))
    report("net_price reflects new discount", data.get("net_price") == 44.99,
           f"net_price={data.get('net_price')}")
else:
    report("PUT update", False, f"Got {resp.status_code}: {resp.text}")


# ═════════════════════════════════════════════════════════════════════════════
# TEST 6: PATCH (partial update)
# ═════════════════════════════════════════════════════════════════════════════
print("\n═══ TEST 6: PATCH partial update ═══")

patch_payload = {
    "status": "archived"
}

resp = client.patch("/api/v1/books/1", json=patch_payload)
print(f"  Status: {resp.status_code}")

if resp.status_code == 200:
    data = resp.json()
    report("HTTP 200 OK", True)
    report("Status updated to archived", data["status"] == "archived", data["status"])
    report("Title unchanged (partial update)", data["title"] == "The Pragmatic Programmer (2nd Ed)",
           data["title"])
    report("Price unchanged", data["price"] == 59.99, str(data["price"]))
else:
    report("PATCH update", False, f"Got {resp.status_code}: {resp.text}")


# ═════════════════════════════════════════════════════════════════════════════
# TEST 7: DELETE
# ═════════════════════════════════════════════════════════════════════════════
print("\n═══ TEST 7: DELETE a book ═══")

resp = client.delete("/api/v1/books/2")
print(f"  Status: {resp.status_code}")
report("HTTP 204 No Content", resp.status_code == 204, f"Got {resp.status_code}")

# Verify deletion
resp_check = client.get("/api/v1/books/2")
report("Deleted book returns 404", resp_check.status_code == 404, f"Got {resp_check.status_code}")

# Verify remaining count
resp_list = client.get("/api/v1/books/")
if resp_list.status_code == 200:
    data = resp_list.json()
    report("Total is now 1", data["total"] == 1, f"total={data['total']}")


# ═════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "═" * 60)
passed = sum(1 for _, ok in results if ok)
failed = sum(1 for _, ok in results if not ok)
total = len(results)

print(f"  RESULTS: {passed}/{total} passed, {failed} failed")

if failed > 0:
    print("\n  Failed tests:")
    for name, ok in results:
        if not ok:
            print(f"    ✗  {name}")

print("═" * 60)

# Exit with non-zero code if any tests failed
sys.exit(0 if failed == 0 else 1)
