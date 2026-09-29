from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import media
from app.deps import get_current_active_user, get_db
from app.genealogy import children_of, siblings_of, union_children, unions_of
from app.models import Person, User as UserModel, Union
from app.schemas import PersonCreate, PersonUpdate
from app.serializers import (
    GENDERS,
    person_summary,
    photo_out,
    primary_photo_map,
    story_out,
    union_out,
)

router = APIRouter(prefix="/api/persons", tags=["persons"])


def _get_person_or_404(db: Session, person_id: int) -> Person:
    person = db.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


def _validate_parent(db: Session, person_id: Optional[int], field: str) -> None:
    if person_id is None:
        return
    if not db.get(Person, person_id):
        raise HTTPException(status_code=400, detail=f"{field} does not exist")


@router.get("")
def list_persons(
    q: Optional[str] = None,
    gender: Optional[str] = None,
    is_living: Optional[bool] = None,
    limit: int = Query(default=500, ge=1, le=2000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Person)
    if q and q.strip():
        like = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Person.first_name.ilike(like),
                Person.last_name.ilike(like),
                Person.maiden_name.ilike(like),
                Person.birth_place.ilike(like),
                Person.death_place.ilike(like),
                Person.occupation.ilike(like),
            )
        )
    if gender:
        query = query.filter(Person.gender == gender)
    if is_living is not None:
        query = query.filter(Person.is_living.is_(is_living))

    total = query.count()
    persons = (
        query.order_by(
            Person.last_name.is_(None),
            Person.last_name,
            Person.first_name,
            Person.birth_date,
        )
        .offset(offset)
        .limit(limit)
        .all()
    )
    photo_map = primary_photo_map(db, [p.id for p in persons])
    return {
        "total": total,
        "items": [person_summary(p, photo_map.get(p.id)) for p in persons],
    }


@router.get("/{person_id}")
def get_person(person_id: int, db: Session = Depends(get_db)):
    person = _get_person_or_404(db, person_id)

    father = db.get(Person, person.father_id) if person.father_id else None
    mother = db.get(Person, person.mother_id) if person.mother_id else None
    siblings = siblings_of(db, person)
    person_unions = unions_of(db, person.id)
    children = children_of(db, person.id)

    union_details = []
    involved_ids = {person.id}
    for union in person_unions:
        kids = union_children(db, union)
        union_details.append((union, kids))
        involved_ids.update(k for k in [union.partner_a_id, union.partner_b_id] if k)
        involved_ids.update(c.id for c in kids)

    involved_ids.update(c.id for c in children)
    for relative in (father, mother):
        if relative:
            involved_ids.add(relative.id)
    involved_ids.update(s.id for s in siblings)

    photo_map = primary_photo_map(db, involved_ids)

    return {
        **person_summary(person, photo_map.get(person.id)),
        "bio": person.bio,
        "father": person_summary(father, photo_map.get(father.id)) if father else None,
        "mother": person_summary(mother, photo_map.get(mother.id)) if mother else None,
        "siblings": [person_summary(s, photo_map.get(s.id)) for s in siblings],
        "children": [person_summary(c, photo_map.get(c.id)) for c in children],
        "unions": [
            union_out(union, db.get(Person, union.partner_a_id),
                      db.get(Person, union.partner_b_id) if union.partner_b_id else None,
                      kids, photo_map)
            for union, kids in union_details
        ],
        "photos": [photo_out(ph) for ph in person.photos],
        "stories": [story_out(st) for st in person.stories],
    }


@router.post("", status_code=201)
def create_person(
    payload: PersonCreate,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_active_user),
):
    if payload.gender and payload.gender not in GENDERS:
        raise HTTPException(status_code=400, detail="Invalid gender value")
    _validate_parent(db, payload.father_id, "father_id")
    _validate_parent(db, payload.mother_id, "mother_id")

    person = Person(**payload.model_dump())
    db.add(person)
    db.commit()
    db.refresh(person)
    return person_summary(person)


@router.put("/{person_id}")
def update_person(
    person_id: int,
    payload: PersonUpdate,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_active_user),
):
    person = _get_person_or_404(db, person_id)
    data = payload.model_dump(exclude_unset=True)

    if "gender" in data and data["gender"] and data["gender"] not in GENDERS:
        raise HTTPException(status_code=400, detail="Invalid gender value")
    for field in ("father_id", "mother_id"):
        if field in data:
            if data[field] == person_id:
                raise HTTPException(status_code=400, detail="A person cannot be their own parent")
            _validate_parent(db, data[field], field)

    for key, value in data.items():
        setattr(person, key, value)
    db.commit()
    db.refresh(person)
    return person_summary(person)


@router.delete("/{person_id}", status_code=204)
def delete_person(
    person_id: int,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_active_user),
):
    person = _get_person_or_404(db, person_id)
    db.delete(person)
    db.commit()
    media.delete_person_files(person_id)
    return None
