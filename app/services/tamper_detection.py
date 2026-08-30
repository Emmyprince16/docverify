"""
Tamper/authenticity detection service.

Two forensic checks for PDFs:
1. Multiple "%%EOF" markers — PDFs are structured so that edits are
   often appended rather than rewriting the file from scratch. A PDF
   with more than one %%EOF marker has likely been modified and
   re-saved after its original creation.
2. Metadata inconsistency — comparing a PDF's CreationDate and
   ModDate (modification date) fields. A ModDate significantly after
   the CreationDate suggests the file was edited after it was made.

Together these give an explainable tamper_score from 0.0 (clean) to
1.0 (strong signs of tampering), plus a list of specific findings.
"""

import os
from pypdf import PdfReader


def check_tamper(file_path: str) -> dict:
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension != ".pdf":
        return {
            "tamper_score": 0.0,
            "findings": ["Tamper detection currently supports PDF files only."],
        }

    findings = []
    score = 0.0

    # Check 1: multiple %%EOF markers
    with open(file_path, "rb") as f:
        content = f.read()

    eof_count = content.count(b"%%EOF")
    if eof_count > 1:
        findings.append(
            f"Document contains {eof_count} end-of-file markers, "
            "suggesting it was edited and re-saved after its original creation."
        )
        score += 0.5

    # Check 2: metadata date inconsistency
    try:
        reader = PdfReader(file_path)
        metadata = reader.metadata

        creation_date = metadata.get("/CreationDate") if metadata else None
        mod_date = metadata.get("/ModDate") if metadata else None

        if creation_date and mod_date and creation_date != mod_date:
            findings.append(
                "Modification date differs from creation date, "
                "indicating the file was changed after it was first created."
            )
            score += 0.3
    except Exception:
        findings.append("Could not read PDF metadata (file may be malformed or encrypted).")
        score += 0.2

    if not findings:
        findings.append("No signs of tampering detected.")

    return {
        "tamper_score": min(score, 1.0),
        "findings": findings,
    }