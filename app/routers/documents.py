"""
Routes for uploading a document and running verification checks on it:
digital signature (PKI), hash comparison against prior uploads, and
tamper detection.
"""

import os
import hashlib
import shutil

from fastapi import APIRouter, Request, Form, UploadFile, File, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Signer, Document, DigitalSigCheck, TamperCheck
from app.services.digital_signature import check_digital_signature
from app.services.tamper_detection import check_tamper

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

UPLOAD_DIR = "app/static/uploads"


@router.get("/verify")
def show_upload_form(request: Request, db: Session = Depends(get_db)):
    signers = db.query(Signer).all()
    return templates.TemplateResponse(request, "verify.html", {"signers": signers})


@router.post("/verify")
def upload_document(
    request: Request,
    signer_id: str = Form(...),
    document_file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    saved_path = os.path.join(UPLOAD_DIR, document_file.filename)
    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(document_file.file, buffer)

    with open(saved_path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    previous_document = (
        db.query(Document)
        .filter(Document.filename == document_file.filename)
        .order_by(Document.uploaded_at.desc())
        .first()
    )

    if previous_document:
        hash_match = previous_document.file_hash == file_hash
        is_first_upload = False
    else:
        hash_match = True
        is_first_upload = True

    new_document = Document(
        signer_id=signer_id,
        filename=document_file.filename,
        file_path=saved_path,
        file_hash=file_hash,
    )
    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    result = check_digital_signature(saved_path)

    sig_check = DigitalSigCheck(
        document_id=new_document.id,
        has_digital_signature=result["has_digital_signature"],
        cert_valid=result["cert_valid"],
        hash_match=hash_match,
        signer_common_name=result["signer_common_name"],
    )
    db.add(sig_check)
    db.commit()

    tamper_result = check_tamper(saved_path)

    tamper_check = TamperCheck(
        document_id=new_document.id,
        tamper_score=tamper_result["tamper_score"],
        findings="|".join(tamper_result["findings"]),
    )
    db.add(tamper_check)
    db.commit()

    return templates.TemplateResponse(
        request,
        "verify_result.html",
        {
            "document": new_document,
            "sig_check": sig_check,
            "tamper_check": tamper_check,
            "is_first_upload": is_first_upload,
        },
    )