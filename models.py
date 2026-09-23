from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Date, Time, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    customer = "customer"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.customer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    visits = relationship("Visit", back_populates="user")


class PropertyType(str, enum.Enum):
    apartment = "apartment"
    house = "house"
    plot = "plot"
    commercial = "commercial"


class PropertyStatus(str, enum.Enum):
    available = "available"
    sold = "sold"
    rented = "rented"


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    location = Column(String, nullable=False)
    property_type = Column(Enum(PropertyType), nullable=False)
    bedrooms = Column(Integer, default=0)
    bathrooms = Column(Integer, default=0)
    area = Column(Float, nullable=True)
    status = Column(Enum(PropertyStatus), default=PropertyStatus.available)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    photos = relationship("PropertyPhoto", back_populates="property", cascade="all, delete-orphan")
    visits = relationship("Visit", back_populates="property")


class PropertyPhoto(Base):
    __tablename__ = "property_photos"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    url = Column(String, nullable=False)
    is_primary = Column(Boolean, default=False)

    property = relationship("Property", back_populates="photos")


class VisitStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"


class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    visit_date = Column(Date, nullable=False)
    visit_time = Column(Time, nullable=False)
    status = Column(Enum(VisitStatus), default=VisitStatus.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="visits")
    property = relationship("Property", back_populates="visits")
