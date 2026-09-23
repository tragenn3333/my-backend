from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import auth, users, properties, visits

# Creates tables if they don't exist (fine for dev; use Alembic migrations later for production)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Real Estate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict this to your frontend's URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(properties.router)
app.include_router(visits.router)


@app.get("/")
def root():
    return {"status": "Real Estate API is running"}
