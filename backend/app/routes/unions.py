from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_current_active_user, get_db
from app.genealogy import union_children
from app.models import Person, User as UserModel, Union
from app.schemas import UnionCreate, UnionUpdate
from app.serializers import UNION_STATUSES, primary_photo_map, union_out

router = APIRouter(prefix="/api/unions", tags=["unions"])


def _validate_partners(db: Session, a: int, b: int | None) -> None:
    if not db.get(Person, a):
        raise HTTPException(status_code=400, detail="partner_a_id does not exist")
    if b is not None:
        if b == a:
            raise HTTPException(status_code=400, detail="A person cannot be their own partner")
        if not db.get(Person, b):
            raise HTTPException(status_code=400, detail="partner_b_id does not exist")


def union_payload(db: Session, union: Union) -> dict:
    kids = union_children(db, union)
    ids = [union.partner_a_id, union.partner_b_id] + [c.id for c in kids]
    photo_map = primary_photo_map(db, [i for i in ids if i])
    return union_out(
        union,
        db.get(Person, union.partner_a_id),
        db.get(Person, union.partner_b_id) if union.partner_b_id else None,
        kids,
        photo_map,
    )


@router.get("")
def list_unions(db: Session = Depends(get_db)):
    unions = (
        db.query(Union)
        .order_by(Union.start_date.is_(None), Union.start_date, Union.id)
        .all()
    )
    return [union_payload(db, u) for u in unions]


@router.get("/{union_id}")
def get_union(union_id: int, db: Session = Depends(get_db)):
    union = db.get(Union, union_id)
    if not union:
        raise HTTPException(status_code=404, detail="Union not found")
    return union_payload(db, union)


@router.post("", status_code=201)
def create_union(
    payload: UnionCreate,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_active_user),
):
    if payload.status not in UNION_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid union status")
    _validate_partners(db, payload.partner_a_id, payload.partner_b_id)

    union = Union(**payload.model_dump())
    db.add(union)
    db.commit()
    db.refresh(union)
    return union_payload(db, union)


@router.put("/{union_id}")
def update_union(
    union_id: int,
    payload: UnionUpdate,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_active_user),
):
    union = db.get(Union, union_id)
    if not union:
        raise HTTPException(status_code=404, detail="Union not found")

    data = payload.model_dump(exclude_unset=True)
    if "status" in data and data["status"] not in UNION_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid union status")

    partner_a = data.get("partner_a_id", union.partner_a_id)
    if "partner_b_id" in data:
        partner_b = data["partner_b_id"]
    else:
        partner_b = union.partner_b_id
    _validate_partners(db, partner_a, partner_b)

    for key, value in data.items():
        setattr(union, key, value)
    db.commit()
    db.refresh(union)
    return union_payload(db, union)


@router.delete("/{union_id}", status_code=204)
def delete_union(
    union_id: int,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_active_user),
):
    union = db.get(Union, union_id)
    if not union:
        raise HTTPException(status_code=404, detail="Union not found")
    db.delete(union)
    db.commit()
    return None
