import os

from sqlalchemy.orm import Session

from app.auth import get_password_hash
from app.database import Base, SessionLocal, engine
from app.models import Person, Union, User


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _seed_admin(db: Session) -> None:
    if db.query(User).count() > 0:
        print("[seed] Users already exist, skipping admin creation")
        return
    username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD", "family123")
    db.add(User(username=username, hashed_password=get_password_hash(password)))
    db.commit()
    print(f"[seed] Created admin user: {username}")


def _person(db: Session, first, last, **kwargs) -> Person:
    person = Person(first_name=first, last_name=last, **kwargs)
    db.add(person)
    db.flush()
    return person


def _seed_demo(db: Session) -> None:
    print("[seed] Seeding demo family (SEED_DEMO_DATA is on)")

    samuel = _person(db, "Samuel", "Okonkwo", gender="male", birth_date="1920",
                     death_date="1998", birth_place="Enugu", occupation="Farmer",
                     is_living=False, bio="Patriarch of the Okonkwo family.")
    grace = _person(db, "Grace", "Okonkwo", maiden_name="Adeyemi", gender="female",
                    birth_date="1925", death_date="2010", birth_place="Onitsha",
                    occupation="Trader", is_living=False)
    david = _person(db, "David", "Okonkwo", gender="male", birth_date="1948",
                    birth_place="Enugu", occupation="Engineer",
                    father_id=samuel.id, mother_id=grace.id)
    ruth = _person(db, "Ruth", "Eze", maiden_name="Okonkwo", gender="female",
                   birth_date="1951", birth_place="Enugu", occupation="Teacher",
                   father_id=samuel.id, mother_id=grace.id)

    mary = _person(db, "Mary", "Okonkwo", maiden_name="Bello", gender="female",
                   birth_date="1950", occupation="Nurse")
    esther = _person(db, "Esther", "Okonkwo", maiden_name="Nwosu", gender="female",
                     birth_date="1960", occupation="Accountant")
    peter = _person(db, "Peter", "Eze", gender="male", birth_date="1949",
                    occupation="Civil Servant")

    michael = _person(db, "Michael", "Okonkwo", gender="male", birth_date="1974",
                      father_id=david.id, mother_id=mary.id)
    sarah = _person(db, "Sarah", "Okonkwo", gender="female", birth_date="1977",
                    father_id=david.id, mother_id=mary.id)
    jonathan = _person(db, "Jonathan", "Okonkwo", gender="male", birth_date="1990",
                       father_id=david.id, mother_id=esther.id)
    daniel = _person(db, "Daniel", "Eze", gender="male", birth_date="1980",
                     father_id=peter.id, mother_id=ruth.id)

    db.add_all([
        Union(partner_a_id=samuel.id, partner_b_id=grace.id, status="married",
              start_date="1945"),
        Union(partner_a_id=david.id, partner_b_id=mary.id, status="divorced",
              start_date="1972", end_date="1985"),
        Union(partner_a_id=david.id, partner_b_id=esther.id, status="married",
              start_date="1988"),
        Union(partner_a_id=peter.id, partner_b_id=ruth.id, status="married",
              start_date="1975"),
    ])
    db.commit()
    print(f"[seed] Demo family created: Samuel, Grace, David, Ruth, Michael, "
          f"Sarah, Jonathan, Daniel")


def seed_database() -> None:
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        _seed_admin(db)
        if env_bool("SEED_DEMO_DATA", False) and db.query(Person).count() == 0:
            _seed_demo(db)
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
