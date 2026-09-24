from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
import models  # noqa: F401  (needed so the tables get created)
from routes_auth import router as auth_router
from routes_properties import router as properties_router
from routes_visits import router as visits_router


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

app.include_router(auth_router)
app.include_router(properties_router)
app.include_router(visits_router)


@app.get("/")
def root():
    return {"status": "Real Estate API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
