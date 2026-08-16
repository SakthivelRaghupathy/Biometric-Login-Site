# app/routers/webauthn_router.py
from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.schemas.webauthn_schema import (
    WebAuthnRegisterStartRequest,
    WebAuthnRegisterFinishRequest,
    WebAuthnLoginStartRequest,
    WebAuthnLoginFinishRequest
)
from app.services.webauthn_service import WebAuthnService

webauthn_router = Blueprint("webauthn_router", __name__)


@webauthn_router.route("/webauthn/register/start", methods=["POST"])
def register_start():
    """
    Step 1: Instantiates registration parameters for the biometric hardware.
    """
    try:
        # Validate incoming payload using Pydantic
        body = WebAuthnRegisterStartRequest(**(request.get_json() or {}))
        
        # Call the fido2 service layer
        response_data = WebAuthnService.start_registration(body.username)
        return jsonify(response_data), 200
        
    except ValidationError as e:
        return jsonify({"success": False, "message": "Invalid request format", "details": e.errors()}), 400
    except ValueError as val_err:
        return jsonify({"success": False, "message": str(val_err)}), 400
    except Exception as err:
        return jsonify({"success": False, "message": f"Server processing error: {str(err)}"}), 500


@webauthn_router.route("/webauthn/register/finish", methods=["POST"])
def register_finish():
    """
    Step 2: Cryptographically validates the physical key response signature.
    """
    try:
        body = WebAuthnRegisterFinishRequest(**(request.get_json() or {}))
        
        response_data = WebAuthnService.finish_registration(body.username, body.credential)
        return jsonify(response_data), 200
        
    except ValidationError as e:
        return jsonify({"success": False, "message": "Invalid request format", "details": e.errors()}), 400
    except ValueError as val_err:
        return jsonify({"success": False, "message": str(val_err)}), 400
    except Exception as err:
        return jsonify({"success": False, "message": f"Biometric verification failed: {str(err)}"}), 500


@webauthn_router.route("/webauthn/login/start", methods=["POST"])
def login_start():
    """
    Step 3: Fetches registered keys and creates a biometric login challenge.
    """
    try:
        body = WebAuthnLoginStartRequest(**(request.get_json() or {}))
        
        response_data = WebAuthnService.start_login(body.username)
        return jsonify(response_data), 200
        
    except ValidationError as e:
        return jsonify({"success": False, "message": "Invalid request format", "details": e.errors()}), 400
    except ValueError as val_err:
        return jsonify({"success": False, "message": str(val_err)}), 400
    except Exception as err:
        return jsonify({"success": False, "message": f"Server processing error: {str(err)}"}), 500


@webauthn_router.route("/webauthn/login/finish", methods=["POST"])
def login_finish():
    """
    Step 4: Validates the hardware response signature payload.
    """
    try:
        body = WebAuthnLoginFinishRequest(**(request.get_json() or {}))
        
        response_data = WebAuthnService.finish_login(body.username, body.credential)
        return jsonify(response_data), 200
        
    except ValidationError as e:
        return jsonify({"success": False, "message": "Invalid request format", "details": e.errors()}), 400
    except ValueError as val_err:
        return jsonify({"success": False, "message": str(val_err)}), 400
    except Exception as err:
        return jsonify({"success": False, "message": f"Biometric authentication failed: {str(err)}"}), 500