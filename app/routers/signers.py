"""
Routes for registering signers and storing their reference signature.
This reference signature is what the ML module will later compare
new signatures against.
"""

import os
import shutil

from fastapi import APIRouter, Request, Form, UploadFile, File, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Signer

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

REFERENCE_DIR = "app/static/references"


@router.get("/register")
def show_register_form(request: Request):
    return templates.TemplateResponse(request, "register.html")


@router.post("/register")
def register_signer(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    reference_signature: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    os.makedirs(REFERENCE_DIR, exist_ok=True)

    file_extension = reference_signature.filename.split(".")[-1]
    saved_filename = f"{email}_reference.{file_extension}"
    saved_path = os.path.join(REFERENCE_DIR, saved_filename)

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(reference_signature.file, buffer)

    new_signer = Signer(
        full_name=full_name,
        email=email,
        reference_signature_path=saved_path,
    )
    db.add(new_signer)
    db.commit()
    db.refresh(new_signer)

    return templates.TemplateResponse(
        request, "register_success.html", {"signer": new_signer}
    )