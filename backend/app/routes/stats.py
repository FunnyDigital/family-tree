from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_db
from app.genealogy import generation_map
from app.models import Person, Photo, Story, Union

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    persons = db.query(Person).all()
    unions = db.query(Union).all()

    generations = 0
    if persons:
        gen = generation_map(persons, unions)
        generations = max(gen.values()) + 1 if gen else 0

    living = sum(1 for p in persons if p.is_living)
    deceased = len(persons) - living
    with_photos = (
        db.query(Photo.person_id).distinct().count()
    )

    return {
        "total_people": len(persons),
        "total_unions": len(unions),
        "total_photos": db.query(Photo).count(),
        "total_stories": db.query(Story).count(),
        "generations": generations,
        "living": living,
        "deceased": deceased,
        "people_with_photos": with_photos,
    }
