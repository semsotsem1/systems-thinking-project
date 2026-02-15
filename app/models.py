from datetime import datetime, UTC
from typing import Optional

from sqlmodel import Field, SQLModel


class NoteBase(SQLModel):
    title: str
    body: str


class Note(NoteBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

class NoteCreate(NoteBase):
    pass


class NoteUpdate(SQLModel):
    title: Optional[str] = None
    body: Optional[str] = None