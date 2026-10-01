from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_db
from app.genealogy import generation_map, implied_couples
from app.models import Person, Photo, Story, Union

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    persons = db.query(Person).all()
    unions = db.query(Union).all()

    # A marriage is a recorded union or a couple who share a child, counted once per couple.
    recorded = {
        (min(union.partner_a_id, union.partner_b_id), max(union.partner_a_id, union.partner_b_id))
        for union in unions
        if union.partner_b_id is not None
    }
    marriages = recorded | implied_couples(persons)

    generations = 0
    if persons:
        gen = generation_map(persons, unions)
        generations = max(gen.values()) + 1 if gen else 0

    living = sum(1 for p in persons if p.is_living)
    deceased = len(persons) - living
    with_photos = db.query(Photo.person_id).distinct().count()

    return {
        "total_people": len(persons),
        "total_marriages": len(marriages),
        "total_photos": db.query(Photo).count(),
        "total_stories": db.query(Story).count(),
        "generations": generations,
        "living": living,
        "deceased": deceased,
        "people_with_photos": with_photos,
    }
