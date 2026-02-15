from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

from app.main import app
from app.db import get_session


TEST_DB_URL = "sqlite:///./test.db"
connect_args = {"check_same_thread": False}
engine = create_engine(TEST_DB_URL, connect_args=connect_args)


def override_get_session():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


def test_crud_flow():
    client = TestClient(app)

    # create
    r = client.post("/notes", json={"title": "t1", "body": "b1"})
    assert r.status_code == 200
    note = r.json()
    note_id = note["id"]
    assert note["title"] == "t1"

    # list
    r = client.get("/notes")
    assert r.status_code == 200
    assert len(r.json()) >= 1

    # get
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    assert r.json()["body"] == "b1"

    # update
    r = client.put(f"/notes/{note_id}", json={"body": "b2"})
    assert r.status_code == 200
    assert r.json()["body"] == "b2"

    # delete
    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 200
    assert r.json() == {"ok": True}

    # get after delete -> 404
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404