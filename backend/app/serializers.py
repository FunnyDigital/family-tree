from typing import Iterable, Optional

from sqlalchemy.orm import Session

from app.models import Person, Photo, Story, Union

GENDERS = {"male", "female", "other", "unknown"}
UNION_STATUSES = {"married", "partnered", "divorced", "widowed", "separated"}


def full_name(person: Person) -> str:
    parts = [person.first_name or "", person.last_name or ""]
    name = " ".join(p for p in parts if p).strip()
    return name or "Unnamed"


def year_of(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    digits = ""
    for ch in value:
        if ch.isdigit():
            digits += ch
        elif digits:
            break
    return digits[:4] if len(digits) >= 4 else (digits or None)


def life_span(person: Person) -> str:
    birth = year_of(person.birth_date)
    death = year_of(person.death_date)
    if birth and death:
        return f"{birth}–{death}"
    if birth and not person.is_living:
        return f"{birth}–"
    if birth:
        return f"b. {birth}"
    if death:
        return f"d. {death}"
    return ""


def photo_url(photo: Optional[Photo], thumb: bool = True) -> Optional[str]:
    if not photo:
        return None
    name = (photo.thumb_filename or photo.filename) if thumb else photo.filename
    return f"/media/{name}"


def photo_out(photo: Photo) -> dict:
    return {
        "id": photo.id,
        "person_id": photo.person_id,
        "url": photo_url(photo, thumb=False),
        "thumb_url": photo_url(photo, thumb=True),
        "caption": photo.caption,
        "original_name": photo.original_name,
        "is_primary": photo.is_primary,
        "sort_order": photo.sort_order,
    }


def story_out(story: Story) -> dict:
    return {
        "id": story.id,
        "person_id": story.person_id,
        "title": story.title,
        "body": story.body,
        "created_at": story.created_at,
        "updated_at": story.updated_at,
    }


def person_summary(person: Person, photo: Optional[Photo] = None) -> dict:
    return {
        "id": person.id,
        "first_name": person.first_name,
        "last_name": person.last_name,
        "maiden_name": person.maiden_name,
        "full_name": full_name(person),
        "gender": person.gender,
        "birth_date": person.birth_date,
        "death_date": person.death_date,
        "birth_place": person.birth_place,
        "death_place": person.death_place,
        "occupation": person.occupation,
        "is_living": person.is_living,
        "life_span": life_span(person),
        "father_id": person.father_id,
        "mother_id": person.mother_id,
        "photo_url": photo_url(photo),
    }


def primary_photo_map(db: Session, person_ids: Iterable[int]) -> dict[int, Photo]:
    ids = list(person_ids)
    if not ids:
        return {}
    photos = (
        db.query(Photo)
        .filter(Photo.person_id.in_(ids))
        .order_by(Photo.is_primary.desc(), Photo.sort_order.asc(), Photo.id.asc())
        .all()
    )
    result: dict[int, Photo] = {}
    for photo in photos:
        result.setdefault(photo.person_id, photo)
    return result


def union_out(union: Union, partner_a: Optional[Person], partner_b: Optional[Person],
              children: list[Person], photo_map: dict[int, Photo]) -> dict:
    return {
        "id": union.id,
        "status": union.status,
        "start_date": union.start_date,
        "end_date": union.end_date,
        "notes": union.notes,
        "partner_a": person_summary(partner_a, photo_map.get(partner_a.id))
        if partner_a
        else None,
        "partner_b": person_summary(partner_b, photo_map.get(partner_b.id))
        if partner_b
        else None,
        "children": [person_summary(c, photo_map.get(c.id)) for c in children],
    }
