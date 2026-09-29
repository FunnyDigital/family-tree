from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import Person, Union


def _birth_order(query):
    return query.order_by(
        Person.birth_date.is_(None), Person.birth_date, Person.first_name
    )


def children_of(db: Session, person_id: int) -> list[Person]:
    query = db.query(Person).filter(
        or_(Person.father_id == person_id, Person.mother_id == person_id)
    )
    return _birth_order(query).all()


def unions_of(db: Session, person_id: int) -> list[Union]:
    return (
        db.query(Union)
        .filter(or_(Union.partner_a_id == person_id, Union.partner_b_id == person_id))
        .order_by(Union.start_date.is_(None), Union.start_date, Union.id)
        .all()
    )


def union_children(db: Session, union: Union) -> list[Person]:
    a, b = union.partner_a_id, union.partner_b_id
    query = db.query(Person)
    if b is None:
        query = query.filter(
            or_(
                (Person.father_id == a) & (Person.mother_id.is_(None)),
                (Person.mother_id == a) & (Person.father_id.is_(None)),
            )
        )
    else:
        query = query.filter(
            or_(
                (Person.father_id == a) & (Person.mother_id == b),
                (Person.father_id == b) & (Person.mother_id == a),
            )
        )
    return _birth_order(query).all()


def siblings_of(db: Session, person: Person) -> list[Person]:
    conditions = []
    if person.father_id:
        conditions.append(Person.father_id == person.father_id)
    if person.mother_id:
        conditions.append(Person.mother_id == person.mother_id)
    if not conditions:
        return []
    query = db.query(Person).filter(Person.id != person.id, or_(*conditions))
    return _birth_order(query).all()


def generation_map(persons: list[Person], unions: list[Union]) -> dict[int, int]:
    by_id = {p.id: p for p in persons}
    gen: dict[int, int] = {p.id: 0 for p in persons}

    def raw(pid: int, stack: frozenset[int]) -> int:
        person = by_id.get(pid)
        if person is None or pid in stack:
            return 0
        parents = [x for x in (person.father_id, person.mother_id) if x in by_id]
        if not parents:
            return 0
        next_stack = stack | {pid}
        return max(raw(x, next_stack) for x in parents) + 1

    for person in persons:
        gen[person.id] = raw(person.id, frozenset())

    for _ in range(12):
        changed = False
        for union in unions:
            a, b = union.partner_a_id, union.partner_b_id
            if a in gen and b is not None and b in gen:
                high = max(gen[a], gen[b])
                if gen[a] != high:
                    gen[a] = high
                    changed = True
                if gen[b] != high:
                    gen[b] = high
                    changed = True
        for person in persons:
            parents = [x for x in (person.father_id, person.mother_id) if x in gen]
            if parents:
                want = max(gen[x] for x in parents) + 1
                if gen[person.id] < want:
                    gen[person.id] = want
                    changed = True
        if not changed:
            break

    return gen
