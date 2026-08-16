from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.schemas.otp_schema import (
    OTPRequest,
    OTPVerifyRequest
)

from app.services.auth_service import get_user_by_username

from app.services.otp_service import (
    create_otp,
    store_otp,
    send_otp_email,
    verify_otp
)

otp_router = Blueprint(
    "otp_router",
    __name__,
    url_prefix="/otp"
)


# --------------------------------------------------
# Send OTP
# --------------------------------------------------

@otp_router.route("/send", methods=["POST"])
def send_otp():

    try:

        data = request.get_json()

        validated_data = OTPRequest(**data)

        user = get_user_by_username(
            validated_data.username
        )

        if user is None:

            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404

        email = user["email"]

        otp = create_otp()

        store_otp(
            email=email,
            otp=otp
        )

        email_sent = send_otp_email(

            email=email,

            username=user["username"],

            otp=otp

        )

        if email_sent:

            return jsonify({
                "success": True,
                "message": "OTP sent successfully"
            }), 200

        return jsonify({
            "success": False,
            "message": "Failed to send OTP"
        }), 500

    except ValidationError as e:

        return jsonify({
            "success": False,
            "message": e.errors()
        }), 400

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# --------------------------------------------------
# Verify OTP
# --------------------------------------------------

@otp_router.route("/verify", methods=["POST"])
def verify_otp_route():

    try:

        data = request.get_json()

        validated_data = OTPVerifyRequest(**data)

        user = get_user_by_username(
            validated_data.username
        )

        if user is None:

            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404

        email = user["email"]

        is_valid = verify_otp(

            email=email,

            otp=validated_data.otp

        )

        if is_valid:

            return jsonify({
                "success": True,
                "message": "OTP verified successfully"
            }), 200

        return jsonify({
            "success": False,
            "message": "Invalid or expired OTP"
        }), 400

    except ValidationError as e:

        return jsonify({
            "success": False,
            "message": e.errors()
        }), 400

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500