from app.database import models, schemas
from app.database.schemas import NoteDB, NoteSchema
from app.dependencies import get_db, templates
from app.internal.notes import notes
from fastapi import APIRouter, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import Depends, Form
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND
from typing import List


router = APIRouter(
    prefix="/notes",
    tags=["notes"],
    responses={404: {"description": "Not found"}},
)


@router.post("/add", response_model=NoteDB, status_code=201)
async def create_new_note(request: Request,
                          session: Session = Depends(get_db)) -> templates:
    form = await request.form()
    new_note = schemas.NoteSchema(**dict(form))
    await create_note(note=new_note, session=session)
    return RedirectResponse('/notes', status_code=HTTP_302_FOUND)


@router.get("/add")
async def create_note_form(request: Request):
    return templates.TemplateResponse("notes/note.html",
                                      {"request": request})


async def create_note(note: NoteSchema, session: Session) -> models.Note:
    note_id = await notes.post(session, note)
    response_object = {
        "id": note_id,
        "title": note.title,
        "description": note.description,
        "timestamp": note.timestamp,
    }
    return response_object

test_data = [
    {"id": 1, "title": "something",
     "description": "something else", "timestamp": None},
    {"id": 2, "title": "someone",
     "description": "someone else", "timestamp": None},
]


@router.get("/", response_model=List[NoteDB])
async def read_all_notes(request: Request,
                         session: Session = Depends(get_db)):
    db_notes_data = await notes.get_all(session)
    data = jsonable_encoder(db_notes_data)
    return templates.TemplateResponse(
        "notes/notes.html",
        {'request': request, 'data': data})
    # return db_notes_data


@router.get("/{id}/", response_model=NoteSchema)
async def read_note(id: int, session: Session = Depends(get_db)):
    note = await notes.get(session, id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/{id}/", response_model=NoteDB)
async def update_note(request: Request, id: int, payload: NoteSchema,
                      session: Session = Depends(get_db)):
    note = await notes.get(session, id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    note_id = await notes.put(session, id, payload)
    response_object = {
        "id": note_id,
        "title": payload.title,
        "description": payload.description,
        "timestamp": payload.timestamp,
    }
    return response_object
    # return templates.TemplateResponse(
    #     "notes/note.html", {'request': request, 'data': response_object})


@router.delete("/{id}/", response_model=NoteDB)
async def delete_note(id: int, session: Session = Depends(get_db)):
    note = await notes.get(session, id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    await notes.delete(session, id)
    return note
