from fastapi import FastAPI, Request, Depends, Form, HTTPException
from sqlmodel import select, Session
from app.models import Item
from app.database import get_session, init_db
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/")
async def read_items(request: Request, session: Session = Depends(get_session)):
    items = session.exec(select(Item)).all()
    return templates.TemplateResponse("items_table.html", {"request": request, "items": items})

@app.post("/update")
async def update_item(id: int = Form(...), field: str = Form(...), value: str = Form(...), session: Session = Depends(get_session)):
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if hasattr(item, field):
        setattr(item, field, value)
        session.add(item)
        session.commit()
    return {"status": "success"}

# Route to show the "Create Item" form
@app.get("/items/create")
async def create_item_form(request: Request):
    return templates.TemplateResponse("create_item.html", {"request": request})

# Route to handle the "Create Item" form submission
@app.post("/items/create")
async def create_item(name: str = Form(...), description: str = Form(...), session: Session = Depends(get_session)):
    new_item = Item(name=name, description=description)
    session.add(new_item)
    session.commit()
    session.refresh(new_item)
    return RedirectResponse(url="/", status_code=303)
