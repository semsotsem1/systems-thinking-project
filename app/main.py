from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select

from app.db import init_db, get_session
from app.models import Note, NoteCreate, NoteUpdate

app = FastAPI(title="systems-thinking-project", version="0.1.0")


from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select

from app.db import init_db, get_session
from app.models import Note, NoteCreate, NoteUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="systems-thinking-project", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health():
    return {"ok": True, "degraded": False}


@app.post("/notes", response_model=Note)
def create_note(payload: NoteCreate, session: Session = Depends(get_session)):
    note = Note(**payload.model_dump())
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


@app.get("/notes", response_model=list[Note])
def list_notes(session: Session = Depends(get_session)):
    notes = session.exec(select(Note).order_by(Note.id.desc())).all()
    return notes


@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: int, session: Session = Depends(get_session)):
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="note not found")
    return note


@app.put("/notes/{note_id}", response_model=Note)
def update_note(note_id: int, payload: NoteUpdate, session: Session = Depends(get_session)):
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="note not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(note, k, v)

    session.add(note)
    session.commit()
    session.refresh(note)
    return note


@app.delete("/notes/{note_id}")
def delete_note(note_id: int, session: Session = Depends(get_session)):
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="note not found")

    session.delete(note)
    session.commit()
    return {"ok": True}