from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from sqlalchemy import Column, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import Session

from database import Base, get_db
from models import Property, PropertyPhoto, User
from schemas import PhotoOut
from auth import require_admin

MAX_BYTES = 3 * 1024 * 1024   # 3 MB per photo (the website shrinks photos before upload)
MAX_PHOTOS = 10               # per property
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}


class PhotoBlob(Base):
    """Holds the actual image bytes, linked to a row in property_photos."""
    __tablename__ = "photo_blobs"

    id = Column(Integer, primary_key=True)
    photo_id = Column(Integer, ForeignKey("property_photos.id", ondelete="CASCADE"), unique=True, nullable=False)
    content_type = Column(String, nullable=False)
    data = Column(LargeBinary, nullable=False)


router = APIRouter(tags=["Photos"])


@router.post("/properties/{property_id}/photos", response_model=PhotoOut, status_code=201)
def upload_photo(
    property_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPG, PNG or WebP photos are allowed")

    data = file.file.read(MAX_BYTES + 1)
    if not data:
        raise HTTPException(status_code=400, detail="The photo file is empty")
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=400, detail="Photo is too large (maximum 3 MB)")

    count = db.query(PropertyPhoto).filter(PropertyPhoto.property_id == property_id).count()
    if count >= MAX_PHOTOS:
        raise HTTPException(status_code=400, detail=f"A property can have at most {MAX_PHOTOS} photos")

    photo = PropertyPhoto(property_id=property_id, url="", is_primary=(count == 0))
    db.add(photo)
    db.flush()  # gives the photo its id
    photo.url = f"/photos/{photo.id}/image"
    db.add(PhotoBlob(photo_id=photo.id, content_type=file.content_type, data=data))
    db.commit()
    db.refresh(photo)
    return photo


@router.get("/photos/{photo_id}/image")
def get_photo_image(photo_id: int, db: Session = Depends(get_db)):
    blob = db.query(PhotoBlob).filter(PhotoBlob.photo_id == photo_id).first()
    if not blob:
        raise HTTPException(status_code=404, detail="Photo not found")
    return Response(
        content=bytes(blob.data),
        media_type=blob.content_type,
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.patch("/photos/{photo_id}/primary", response_model=PhotoOut)
def set_cover_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    photo = db.query(PropertyPhoto).filter(PropertyPhoto.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    db.query(PropertyPhoto).filter(PropertyPhoto.property_id == photo.property_id).update({"is_primary": False})
    photo.is_primary = True
    db.commit()
    db.refresh(photo)
    return photo


@router.delete("/photos/{photo_id}", status_code=204)
def delete_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    photo = db.query(PropertyPhoto).filter(PropertyPhoto.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    was_cover = photo.is_primary
    property_id = photo.property_id
    db.query(PhotoBlob).filter(PhotoBlob.photo_id == photo_id).delete()
    db.delete(photo)
    db.commit()

    if was_cover:
        nxt = (
            db.query(PropertyPhoto)
            .filter(PropertyPhoto.property_id == property_id)
            .order_by(PropertyPhoto.id)
            .first()
        )
        if nxt:
            nxt.is_primary = True
            db.commit()
    return Response(status_code=204)
