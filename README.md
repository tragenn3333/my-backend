# Real Estate Backend (Step 1)

FastAPI + PostgreSQL + SQLAlchemy backend with JWT auth, properties CRUD, and visit booking.

## What's included
- User register/login with JWT (`/auth/register`, `/auth/login`)
- Current user info (`/users/me`)
- Properties CRUD (`/properties`) — create/update/delete are admin-only
- Visit booking (`/visits`) with slot-clash checking
- Admin role support (set manually in the DB for now — see below)

## 1. Install PostgreSQL

**Option A — Docker (easiest):**
```bash
docker compose up -d
```
This starts Postgres on `localhost:5432` with user `postgres` / password `postgres` / db `realestate` (matches `.env.example`).

**Option B — Local install:** install PostgreSQL yourself, then create a database:
```bash
createdb realestate
```

## 2. Set up the Python environment

```bash
cd realestate-backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Configure environment variables

```bash
cp .env.example .env
```
Open `.env` and set a real `SECRET_KEY` (any long random string). Adjust `DATABASE_URL` if your Postgres setup differs.

## 4. Run the server

```bash
uvicorn app.main:app --reload
```

Visit **http://127.0.0.1:8000/docs** — this gives you an interactive UI to test every endpoint (register, login, create properties, book visits) without writing any frontend code yet.

## 5. Try it out

1. `POST /auth/register` — create a user
2. `POST /auth/login` (form fields: `username` = your email, `password`) — get a JWT
3. Click **Authorize** in `/docs` and paste the token to test protected routes
4. `POST /properties/` — will fail with 403 until your user has `role = admin`

## Making a user an admin (for now)

Until an admin panel exists, promote a user manually:
```sql
UPDATE users SET role = 'admin' WHERE email = 'you@example.com';
```

## Project structure

```
realestate-backend/
├── app/
│   ├── main.py          # app entrypoint, mounts routers
│   ├── config.py        # env var loading
│   ├── database.py      # SQLAlchemy engine/session
│   ├── models.py        # User, Property, PropertyPhoto, Visit
│   ├── schemas.py        # Pydantic request/response models
│   ├── auth.py           # password hashing, JWT, current-user dependency
│   └── routers/
│       ├── auth.py       # /auth/register, /auth/login
│       ├── users.py      # /users/me
│       ├── properties.py # /properties CRUD
│       └── visits.py     # /visits booking
├── requirements.txt
├── docker-compose.yml     # local Postgres
├── .env.example
└── README.md
```

## Next steps (from the roadmap)
- Photo upload endpoint (`POST /properties/{id}/photos`) + file storage
- Search/filter/pagination on `/properties`
- Email/WhatsApp confirmation on booking
- Alembic migrations instead of `create_all`
- Deployment (Docker image + hosting)

Tell me which of these to build next and I'll add it to this same project.
