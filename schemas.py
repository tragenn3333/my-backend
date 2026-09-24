from pydantic import BaseModel, EmailStr
from datetime import datetime, date, time
from typing import List, Optional
from models import UserRole, PropertyType, PropertyStatus, VisitStatus


# ---- User ----
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---- Property ----
class PropertyCreate(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    location: str
    property_type: PropertyType
    bedrooms: int = 0
    bathrooms: int = 0
    area: Optional[float] = None


class PhotoOut(BaseModel):
    id: int
    url: str
    is_primary: bool

    class Config:
        from_attributes = True


class PropertyOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    price: float
    location: str
    property_type: PropertyType
    bedrooms: int
    bathrooms: int
    area: Optional[float]
    status: PropertyStatus
    created_at: datetime
    photos: List[PhotoOut] = []

    class Config:
        from_attributes = True


# ---- Visit ----
class VisitCreate(BaseModel):
    property_id: int
    visit_date: date
    visit_time: time


class VisitOut(BaseModel):
    id: int
    property_id: int
    user_id: int
    visit_date: date
    visit_time: time
    status: VisitStatus
    created_at: datetime

    class Config:
        from_attributes = True
