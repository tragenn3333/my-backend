from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Property, PropertyStatus, User, Visit, VisitStatus
from schemas import VisitCreate, VisitOut
from auth import get_current_user, require_admin

router = APIRouter(prefix="/visits", tags=["Visits"])


@router.post("", response_model=VisitOut, status_code=201)
def book_visit(
    data: VisitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prop = db.query(Property).filter(Property.id == data.property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    if prop.status != PropertyStatus.available:
        raise HTTPException(status_code=400, detail="Property is not available")
    if data.visit_date < date.today():
        raise HTTPException(status_code=400, detail="Visit date cannot be in the past")

    visit = Visit(
        user_id=current_user.id,
        property_id=data.property_id,
        visit_date=data.visit_date,
        visit_time=data.visit_time,
    )
    db.add(visit)
    db.commit()
    db.refresh(visit)
    return visit


@router.get("/my", response_model=List[VisitOut])
def my_visits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Visit)
        .filter(Visit.user_id == current_user.id)
        .order_by(Visit.visit_date.desc())
        .all()
    )


@router.patch("/{visit_id}/cancel", response_model=VisitOut)
def cancel_visit(
    visit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    visit = db.query(Visit).filter(Visit.id == visit_id).first()
    if not visit or visit.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Visit not found")
    visit.status = VisitStatus.cancelled
    db.commit()
    db.refresh(visit)
    return visit


@router.get("", response_model=List[VisitOut])
def all_visits(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return db.query(Visit).order_by(Visit.visit_date.desc()).all()


@router.patch("/{visit_id}/status", response_model=VisitOut)
def update_visit_status(
    visit_id: int,
    status: VisitStatus,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    visit = db.query(Visit).filter(Visit.id == visit_id).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    visit.status = status
    db.commit()
    db.refresh(visit)
    return visit
