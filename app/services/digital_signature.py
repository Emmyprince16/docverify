"""
Digital signature (PKI) verification service.

A full production implementation would parse embedded PDF signatures
(PAdES) and validate the certificate chain against a trusted
Certificate Authority. For this capstone, we implement a clear,
explainable simulation: it checks the file type and looks for the
markers a real digital signature would embed.
"""

import os


def check_digital_signature(file_path: str) -> dict:
    """
    Returns a dictionary describing whether the file appears to have
    a digital signature and whether it passes basic checks.
    """
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension != ".pdf":
        return {
            "has_digital_signature": False,
            "cert_valid": None,
            "signer_common_name": None,
        }

    with open(file_path, "rb") as f:
        content = f.read()

    has_signature_marker = b"/ByteRange" in content and b"/Sig" in content

    return {
        "has_digital_signature": has_signature_marker,
        "cert_valid": has_signature_marker,
        "signer_common_name": "Not extracted (simplified check)" if has_signature_marker else None,
    }