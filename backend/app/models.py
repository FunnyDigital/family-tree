from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"


class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)
    maiden_name = Column(String(100), nullable=True)
    gender = Column(String(20), nullable=True)
    birth_date = Column(String(32), nullable=True)
    death_date = Column(String(32), nullable=True)
    birth_place = Column(String(160), nullable=True)
    death_place = Column(String(160), nullable=True)
    occupation = Column(String(160), nullable=True)
    bio = Column(Text, nullable=True)
    is_living = Column(Boolean, default=True, nullable=False)

    father_id = Column(Integer, ForeignKey("persons.id", ondelete="SET NULL"), nullable=True)
    mother_id = Column(Integer, ForeignKey("persons.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    photos = relationship(
        "Photo",
        back_populates="person",
        cascade="all, delete-orphan",
        order_by="Photo.sort_order",
    )
    stories = relationship(
        "Story",
        back_populates="person",
        cascade="all, delete-orphan",
        order_by="Story.created_at",
    )

    def __repr__(self):
        return f"<Person {self.first_name} {self.last_name or ''}>".strip()


class Union(Base):
    __tablename__ = "unions"

    id = Column(Integer, primary_key=True, index=True)
    partner_a_id = Column(
        Integer, ForeignKey("persons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    partner_b_id = Column(
        Integer, ForeignKey("persons.id", ondelete="CASCADE"), nullable=True, index=True
    )
    status = Column(String(20), default="married", nullable=False)
    start_date = Column(String(32), nullable=True)
    end_date = Column(String(32), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    def __repr__(self):
        return f"<Union {self.partner_a_id}-{self.partner_b_id}>"


class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(
        Integer, ForeignKey("persons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename = Column(String(255), nullable=False)
    thumb_filename = Column(String(255), nullable=True)
    original_name = Column(String(255), nullable=True)
    caption = Column(String(255), nullable=True)
    is_primary = Column(Boolean, default=False, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    person = relationship("Person", back_populates="photos")

    def __repr__(self):
        return f"<Photo {self.id} person={self.person_id}>"


class Story(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(
        Integer, ForeignKey("persons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title = Column(String(200), nullable=True)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    person = relationship("Person", back_populates="stories")

    def __repr__(self):
        return f"<Story {self.id} person={self.person_id}>"
