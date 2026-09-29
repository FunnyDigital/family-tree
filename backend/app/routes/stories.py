from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_current_active_user, get_db
from app.models import Person, Story, User as UserModel
from app.schemas import StoryCreate, StoryUpdate
from app.serializers import story_out

router = APIRouter(prefix="/api", tags=["stories"])


def _person_or_404(db: Session, person_id: int) -> Person:
    person = db.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


def _story_or_404(db: Session, story_id: int) -> Story:
    story = db.get(Story, story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story


@router.get("/persons/{person_id}/stories")
def list_stories(person_id: int, db: Session = Depends(get_db)):
    _person_or_404(db, person_id)
    stories = (
        db.query(Story)
        .filter(Story.person_id == person_id)
        .order_by(Story.created_at.asc(), Story.id.asc())
        .all()
    )
    return [story_out(s) for s in stories]


@router.post("/persons/{person_id}/stories", status_code=201)
def create_story(
    person_id: int,
    payload: StoryCreate,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_active_user),
):
    _person_or_404(db, person_id)
    story = Story(person_id=person_id, title=payload.title, body=payload.body)
    db.add(story)
    db.commit()
    db.refresh(story)
    return story_out(story)


@router.put("/stories/{story_id}")
def update_story(
    story_id: int,
    payload: StoryUpdate,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_active_user),
):
    story = _story_or_404(db, story_id)
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(story, key, value)
    db.commit()
    db.refresh(story)
    return story_out(story)


@router.delete("/stories/{story_id}", status_code=204)
def delete_story(
    story_id: int,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_active_user),
):
    story = _story_or_404(db, story_id)
    db.delete(story)
    db.commit()
    return None
