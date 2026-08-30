"""
ORM models — these are the tables from the ERD we designed:
Signers -> Documents -> {DigitalSigCheck, SignatureMatch, TamperCheck} -> VerificationReport
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class Signer(Base):
    __tablename__ = "signers"

    id = Column(String, primary_key=True, default=generate_uuid)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    reference_signature_path = Column(String, nullable=True)

    documents = relationship("Document", back_populates="signer")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=generate_uuid)
    signer_id = Column(String, ForeignKey("signers.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_hash = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    signer = relationship("Signer", back_populates="documents")
    digital_sig_check = relationship("DigitalSigCheck", back_populates="document", uselist=False)
    signature_match = relationship("SignatureMatch", back_populates="document", uselist=False)
    tamper_check = relationship("TamperCheck", back_populates="document", uselist=False)
    report = relationship("VerificationReport", back_populates="document", uselist=False)


class DigitalSigCheck(Base):
    __tablename__ = "digital_sig_checks"

    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    has_digital_signature = Column(Boolean, default=False)
    cert_valid = Column(Boolean, nullable=True)
    hash_match = Column(Boolean, nullable=True)
    signer_common_name = Column(String, nullable=True)
    checked_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="digital_sig_check")


class SignatureMatch(Base):
    __tablename__ = "signature_matches"

    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    similarity_score = Column(Float, nullable=False)
    match_result = Column(Boolean, nullable=False)
    threshold_used = Column(Float, nullable=False)
    checked_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="signature_match")


class TamperCheck(Base):
    __tablename__ = "tamper_checks"

    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    tamper_score = Column(Float, nullable=False)
    findings = Column(String, nullable=True)
    checked_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="tamper_check")


class VerificationReport(Base):
    __tablename__ = "verification_reports"

    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    trust_score = Column(Float, nullable=False)
    verdict = Column(String, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="report")