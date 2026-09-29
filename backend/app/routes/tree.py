from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Person, Union
from app.serializers import person_summary, primary_photo_map

router = APIRouter(prefix="/api", tags=["tree"])


@router.get("/tree")
def get_tree(db: Session = Depends(get_db)):
    persons = db.query(Person).all()
    unions = db.query(Union).all()

    photo_map = primary_photo_map(db, [p.id for p in persons])

    person_nodes = []
    for person in persons:
        summary = person_summary(person, photo_map.get(person.id))
        person_nodes.append(
            {
                "id": summary["id"],
                "full_name": summary["full_name"],
                "first_name": summary["first_name"],
                "last_name": summary["last_name"],
                "maiden_name": summary["maiden_name"],
                "gender": summary["gender"],
                "birth_date": summary["birth_date"],
                "death_date": summary["death_date"],
                "life_span": summary["life_span"],
                "is_living": summary["is_living"],
                "occupation": summary["occupation"],
                "photo_url": summary["photo_url"],
                "father_id": summary["father_id"],
                "mother_id": summary["mother_id"],
            }
        )

    union_nodes = [
        {
            "id": u.id,
            "partner_a_id": u.partner_a_id,
            "partner_b_id": u.partner_b_id,
            "status": u.status,
            "start_date": u.start_date,
            "end_date": u.end_date,
        }
        for u in unions
    ]

    return {"persons": person_nodes, "unions": union_nodes}
