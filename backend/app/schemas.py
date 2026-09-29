from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6)


class UserOut(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)


class PersonBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    maiden_name: Optional[str] = Field(default=None, max_length=100)
    gender: Optional[str] = Field(default=None, max_length=20)
    birth_date: Optional[str] = Field(default=None, max_length=32)
    death_date: Optional[str] = Field(default=None, max_length=32)
    birth_place: Optional[str] = Field(default=None, max_length=160)
    death_place: Optional[str] = Field(default=None, max_length=160)
    occupation: Optional[str] = Field(default=None, max_length=160)
    bio: Optional[str] = None
    is_living: bool = True
    father_id: Optional[int] = None
    mother_id: Optional[int] = None


class PersonCreate(PersonBase):
    pass


class PersonUpdate(BaseModel):
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    maiden_name: Optional[str] = Field(default=None, max_length=100)
    gender: Optional[str] = Field(default=None, max_length=20)
    birth_date: Optional[str] = Field(default=None, max_length=32)
    death_date: Optional[str] = Field(default=None, max_length=32)
    birth_place: Optional[str] = Field(default=None, max_length=160)
    death_place: Optional[str] = Field(default=None, max_length=160)
    occupation: Optional[str] = Field(default=None, max_length=160)
    bio: Optional[str] = None
    is_living: Optional[bool] = None
    father_id: Optional[int] = None
    mother_id: Optional[int] = None


class UnionBase(BaseModel):
    partner_a_id: int
    partner_b_id: Optional[int] = None
    status: str = Field(default="married", max_length=20)
    start_date: Optional[str] = Field(default=None, max_length=32)
    end_date: Optional[str] = Field(default=None, max_length=32)
    notes: Optional[str] = None


class UnionCreate(UnionBase):
    pass


class UnionUpdate(BaseModel):
    partner_a_id: Optional[int] = None
    partner_b_id: Optional[int] = None
    status: Optional[str] = Field(default=None, max_length=20)
    start_date: Optional[str] = Field(default=None, max_length=32)
    end_date: Optional[str] = Field(default=None, max_length=32)
    notes: Optional[str] = None


class StoryCreate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)
    body: str = Field(min_length=1)


class StoryUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)
    body: Optional[str] = Field(default=None, min_length=1)


class PhotoUpdate(BaseModel):
    caption: Optional[str] = Field(default=None, max_length=255)
    is_primary: Optional[bool] = None
    sort_order: Optional[int] = None
