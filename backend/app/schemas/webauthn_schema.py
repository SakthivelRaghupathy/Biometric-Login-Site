# app/schemas/webauthn_schema.py
from typing import Any, Dict
from pydantic import BaseModel, Field

# ==========================================================
# Register Start
# ==========================================================
class WebAuthnRegisterStartRequest(BaseModel):
    # Validates that the username is present and formatted correctly
    username: str = Field(..., min_length=3, max_length=50)


class WebAuthnRegisterStartResponse(BaseModel):
    success: bool
    message: str
    options: Dict[str, Any]


# ==========================================================
# Register Finish
# ==========================================================
class WebAuthnRegisterFinishRequest(BaseModel):
    username: str
    # The complex nested JSON structure containing the cryptographic 
    # attestation object sent by the browser's native biometric hardware
    credential: Dict[str, Any]


class WebAuthnRegisterFinishResponse(BaseModel):
    success: bool
    message: str


# ==========================================================
# Login Start
# ==========================================================
class WebAuthnLoginStartRequest(BaseModel):
    username: str


class WebAuthnLoginStartResponse(BaseModel):
    success: bool
    message: str
    options: Dict[str, Any]


# ==========================================================
# Login Finish
# ==========================================================
class WebAuthnLoginFinishRequest(BaseModel):
    username: str
    # The hardware signature payload verifying the user's identity
    credential: Dict[str, Any]


class WebAuthnLoginFinishResponse(BaseModel):
    success: bool
    message: str


# ==========================================================
# Generic Error
# ==========================================================
class WebAuthnErrorResponse(BaseModel):
    success: bool
    message: str