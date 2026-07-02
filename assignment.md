# Assignment: FastAPI CRUD + Git/Docker Basics

**Time:** 3 to 5 hours
**Submit:** GitHub repo link (Part 1) + written answers (Part 2)

---

## Part 1: Build a Book CRUD API

Build a simple CRUD API for a `Book` using FastAPI. Use any database you like (SQLite, MongoDB, even a Python dict is fine). Just explain your choice in the README.

Your `Book` must have at least:
- `title` (required)
- `price` (required, must be positive)
- `discount_price` (optional, must be less than price if given)
- `author` (an object, not just a string)
- `status` (one of: draft, published, archived)

You can add more fields if you want.

**Endpoints needed:**
- Create a book
- List books (with pagination)
- Get one book
- Update a book (full and partial)
- Delete a book

### Pydantic Practice
While building this, make sure you use:
- Separate models for creating, updating, and returning a book (don't reuse one model for everything)
- Field validation (length, positive numbers, etc.) using Pydantic, not manual if-checks
- One custom validator that checks something specific (like discount_price < price)
- A nested model for `author`
- An enum for `status`
- One computed field (something calculated, not stored directly)

### Submit
- Repo with a README (how to run it, what DB you used)
- A few lines in the README: what was tricky about Pydantic and how you solved it

---

## Part 2: Git, GitHub, and Docker (just answer in your own words)

No code needed for this part. Short, clear answers are fine.

1. What's the difference between `git fetch` and `git pull`?
2. Explain what a merge conflict is and how you'd fix one.
3. What's the difference between merge and rebase? When would you use each?
4. What's the difference between squash and fixup commits?
5. What is trunk-based development? How is it different from using long-lived feature branches?
6. How do teams avoid breaking `main` when working directly on it or with short-lived branches?
7. What's your ideal PR process, from creating a branch to merging it?
8. What's the difference between a Docker image and a container?
9. Why do we care about layer caching in a Dockerfile?
10. Should your database run in the same container as your app, or a separate one? Why?

### CI/CD
11. What is CI/CD, in your own words?
12. What would you put in a CI pipeline for this project? (think tests, linting, build steps)
13. What's the difference between continuous delivery and continuous deployment?
14. If a build fails in CI, what should happen to the PR? Should it be allowed to merge?
15. How would you handle secrets (like DB passwords or API keys) in a CI/CD pipeline?

---

## What We're Looking For
- Can you design a clean API and use Pydantic properly, not just make it "work"
- Do you understand git concepts, not just memorized commands
- Can you explain Docker basics clearly
- Can you communicate your reasoning simply
