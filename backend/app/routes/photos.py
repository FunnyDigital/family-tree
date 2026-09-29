from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import media
from app.deps import get_current_active_user, get_db
from app.models import Person, Photo, User as UserModel
from app.schemas import PhotoUpdate
from app.serializers import photo_out

router = APIRouter(prefix="/api", tags=["photos"])


class ReorderPayload(BaseModel):
    order: list[int]


def _person_or_404(db: Session, person_id: int) -> Person:
    person = db.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


def _photo_or_404(db: Session, photo_id: int) -> Photo:
    photo = db.get(Photo, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo


def _clear_primary(db: Session, person_id: int) -> None:
    db.query(Photo).filter(Photo.person_id == person_id, Photo.is_primary.is_(True)).update(
        {"is_primary": False}
    )


@router.get("/persons/{person_id}/photos")
def list_photos(person_id: int, db: Session = Depends(get_db)):
    _person_or_404(db, person_id)
    photos = (
        db.query(Photo)
        .filter(Photo.person_id == person_id)
        .order_by(Photo.sort_order.asc(), Photo.id.asc())
        .all()
    )
    return [photo_out(p) for p in photos]


@router.post("/persons/{person_id}/photos", status_code=201)
def upload_photo(
    person_id: int,
    file: UploadFile = File(...),
    caption: Optional[str] = Form(default=None),
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_active_user),
):
    _person_or_404(db, person_id)
    saved = media.save_photo(person_id, file)

    existing_count = db.query(Photo).filter(Photo.person_id == person_id).count()
    photo = Photo(
        person_id=person_id,
        filename=saved["filename"],
        thumb_filename=saved["thumb_filename"],
        original_name=saved["original_name"],
        caption=caption,
        is_primary=existing_count == 0,
        sort_order=existing_count,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo_out(photo)


@router.put("/photos/{photo_id}")
def update_photo(
    photo_id: int,
    payload: PhotoUpdate,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_active_user),
):
    photo = _photo_or_404(db, photo_id)
    data = payload.model_dump(exclude_unset=True)

    if data.get("is_primary") is True:
        _clear_primary(db, photo.person_id)
    for key, value in data.items():
        setattr(photo, key, value)
    db.commit()
    db.refresh(photo)
    return photo_out(photo)


@router.put("/photos/{photo_id}/primary")
def set_primary(
    photo_id: int,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_active_user),
):
    photo = _photo_or_404(db, photo_id)
    _clear_primary(db, photo.person_id)
    photo.is_primary = True
    db.commit()
    db.refresh(photo)
    return photo_out(photo)


@router.put("/persons/{person_id}/photos/reorder")
def reorder_photos(
    person_id: int,
    payload: ReorderPayload,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_active_user),
):
    _person_or_404(db, person_id)
    photos = db.query(Photo).filter(Photo.person_id == person_id).all()
    by_id = {p.id: p for p in photos}
    for index, photo_id in enumerate(payload.order):
        if photo_id in by_id:
            by_id[photo_id].sort_order = index
    db.commit()
    photos = (
        db.query(Photo)
        .filter(Photo.person_id == person_id)
        .order_by(Photo.sort_order.asc(), Photo.id.asc())
        .all()
    )
    return [photo_out(p) for p in photos]


@router.delete("/photos/{photo_id}", status_code=204)
def delete_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_active_user),
):
    photo = _photo_or_404(db, photo_id)
    person_id = photo.person_id
    was_primary = photo.is_primary
    filename, thumb = photo.filename, photo.thumb_filename

    db.delete(photo)
    db.commit()
    media.delete_photo_files(filename, thumb)

    if was_primary:
        remaining = (
            db.query(Photo)
            .filter(Photo.person_id == person_id)
            .order_by(Photo.sort_order.asc(), Photo.id.asc())
            .first()
        )
        if remaining:
            remaining.is_primary = True
            db.commit()
    return None
