from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.routers import signers, documents
from app.database import Base, engine
from app.models import models

Base.metadata.create_all(bind=engine)


app = FastAPI(title="DocuVerify")
app.include_router(signers.router)
app.include_router(documents.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")