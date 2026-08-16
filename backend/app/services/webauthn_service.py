import os
import json
from typing import Dict, Any
from datetime import datetime
from app.db.mongodb import users_collection
from app.services.auth_service import get_user_by_username

# Using the modern, stable Duo Labs webauthn library (pip install webauthn)
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
)
from webauthn.helpers import(
    bytes_to_base64url,
    base64url_to_bytes,
    options_to_json
)
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    AuthenticatorAttachment,
    UserVerificationRequirement,
    ResidentKeyRequirement,
    PublicKeyCredentialDescriptor
)

# MUST MATCH YOUR BROWSER URL EXACTLY
RP_ID = "localhost"
RP_NAME = "BioSecure Platform"
EXPECTED_ORIGIN = "http://localhost:5500"

class WebAuthnService:

    @staticmethod
    def start_registration(username: str) -> Dict[str, Any]:
        """Step 1: Generates the FIDO2 challenge"""
        user = get_user_by_username(username)
        if not user:
            # Initialize exactly to your flat MongoDB schema
            users_collection.insert_one({
                "username": username,
                "auth": {
                    "fingerprint_registered": False,
                    "face_registered": False,
                    "preferred_method": None
                },
                "webauthn": {}
            })
            user = get_user_by_username(username)

        # Ensure user has a stable unique ID
        user_id = str(user["_id"]).encode('utf-8')

        # Generate clean options using the new library
        options = generate_registration_options(
            rp_id=RP_ID,
            rp_name=RP_NAME,
            user_id=user_id,
            user_name=username,
            user_display_name=username,
            authenticator_selection=AuthenticatorSelectionCriteria(
                authenticator_attachment=AuthenticatorAttachment.PLATFORM,
                user_verification=UserVerificationRequirement.REQUIRED,
                resident_key=ResidentKeyRequirement.PREFERRED
            )
        )

        # Store just the raw challenge string in DB - safe and simple (no enums!)
        users_collection.update_one(
            {"username": username},
            {"$set": {"registration_challenge": bytes_to_base64url(options.challenge)}}
        )

        # Convert to a dictionary for the frontend
        options_dict = json.loads(options_to_json(options))
        
        return {
            "success": True,
            "message": "Challenge generated.",
            "options": {"publicKey": options_dict}
        }

    @staticmethod
    def finish_registration(username: str, credential_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Step 2: Verifies the device signature automatically"""
        user = get_user_by_username(username)
        if not user or "registration_challenge" not in user:
            raise ValueError("No active registration challenge found.")

        expected_challenge = base64url_to_bytes(user["registration_challenge"])

        try:
            # The library handles ALL the bytes, dicts, and ES256 parsing automatically!
            verification = verify_registration_response(
                credential=credential_payload,
                expected_challenge=expected_challenge,
                expected_origin=EXPECTED_ORIGIN,
                expected_rp_id=RP_ID
            )
        except Exception as e:
            raise ValueError(f"Biometric cryptographic verification failed: {str(e)}")

        method = credential_payload.get("method", "fingerprint")
        is_fingerprint = method in ["fingerprint", "both"]
        is_face = method in ["face", "both"]
        
        # Save exact variables to your flat sibling schema
        users_collection.update_one(
            {"username": username},
            {
                "$set": {
                    "webauthn.credential_id": bytes_to_base64url(verification.credential_id),
                    "webauthn.public_key": bytes_to_base64url(verification.credential_public_key),
                    "webauthn.sign_count": verification.sign_count,
                    "webauthn.registered_at": datetime.utcnow(),
                    "auth.fingerprint_registered": is_fingerprint,
                    "auth.face_registered": is_face,
                    "auth.preferred_method": method
                },
                "$unset": {"registration_challenge": ""}
            }
        )

        return {
            "success": True, 
            "message": "Biometric hardware signature approved & stored."
        }

    @staticmethod
    def start_login(username: str) -> Dict[str, Any]:
        """Step 3: Creates a login challenge using stored credentials"""
        user = get_user_by_username(username)
        if not user:
            raise ValueError(f"User '{username}' not found.")

        webauthn_doc = user.get("webauthn", {})
        cred_id_b64 = webauthn_doc.get("credential_id")
        
        if not cred_id_b64:
            raise ValueError("No registered biometric keys found for this user.")

        options = generate_authentication_options(
            rp_id=RP_ID,
            allow_credentials=[
                PublicKeyCredentialDescriptor(id=base64url_to_bytes(cred_id_b64))
            ],
            user_verification=UserVerificationRequirement.PREFERRED
        )

        # Save login challenge
        users_collection.update_one(
            {"username": username},
            {"$set": {"login_challenge": bytes_to_base64url(options.challenge)}}
        )

        options_dict = json.loads(options_to_json(options))

        return {
            "success": True,
            "message": "Login challenge generated.",
            "options": {"publicKey": options_dict}
        }

    @staticmethod
    def finish_login(username: str, assertion_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Step 4: Validates the hardware login signature"""
        user = get_user_by_username(username)
        if not user or "login_challenge" not in user:
            raise ValueError("No active login session found.")

        webauthn_doc = user.get("webauthn", {})
        public_key_b64 = webauthn_doc.get("public_key")
        cred_id_b64 = webauthn_doc.get("credential_id")
        current_sign_count = webauthn_doc.get("sign_count", 0)

        if not public_key_b64 or not cred_id_b64:
            raise ValueError("Missing stored credentials.")

        expected_challenge = base64url_to_bytes(user["login_challenge"])

        try:
            verification = verify_authentication_response(
                credential=assertion_payload,
                expected_challenge=expected_challenge,
                expected_origin=EXPECTED_ORIGIN,
                expected_rp_id=RP_ID,
                credential_public_key=base64url_to_bytes(public_key_b64),
                credential_current_sign_count=current_sign_count
            )
        except Exception as e:
            raise ValueError(f"Authentication signature invalid: {str(e)}")

        # Update sign count and cleanup
        users_collection.update_one(
            {"username": username},
            {
                "$set": {"webauthn.sign_count": verification.new_sign_count},
                "$unset": {"login_challenge": ""}
            }
        )

        return {
            "success": True,
            "message": "Biometric authentication verified successfully!"
        }