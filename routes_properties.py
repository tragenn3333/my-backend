from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from database import get_db
from models import Property, PropertyType, PropertyStatus, User
from schemas import PropertyCreate, PropertyOut
from auth import require_admin

router = APIRouter(prefix="/properties", tags=["Properties"])


@router.get("", response_model=List[PropertyOut])
def list_properties(
    location: Optional[str] = None,
    property_type: Optional[PropertyType] = None,
    status: Optional[PropertyStatus] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    bedrooms: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Property)

    if location:
        query = query.filter(Property.location.ilike(f"%{location}%"))
    if property_type:
        query = query.filter(Property.property_type == property_type)
    if status:
        query = query.filter(Property.status == status)
    if min_price is not None:
        query = query.filter(Property.price >= min_price)
    if max_price is not None:
        query = query.filter(Property.price <= max_price)
    if bedrooms is not None:
        query = query.filter(Property.bedrooms >= bedrooms)

    return query.order_by(Property.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{property_id}", response_model=PropertyOut)
def get_property(property_id: int, db: Session = Depends(get_db)):
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop


@router.post("", response_model=PropertyOut, status_code=201)
def create_property(
    data: PropertyCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    prop = Property(**data.model_dump())
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop


@router.patch("/{property_id}/status", response_model=PropertyOut)
def update_property_status(
    property_id: int,
    status: PropertyStatus,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    prop.status = status
    db.commit()
    db.refresh(prop)
    return prop


@router.delete("/{property_id}", status_code=204)
def delete_property(
    property_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    db.delete(prop)
    db.commit()
    return Response(status_code=204)
