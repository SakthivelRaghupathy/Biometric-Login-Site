from datetime import datetime, timezone


def create_user_model(username: str, email: str):

    now = datetime.now(timezone.utc)

    return {

        "username": username,

        "email": email,

        "auth": {

            "fingerprint_registered": False,

            "face_registered": False,

            "preferred_method": None

        },

        "webauthn": {

            "credential_id": None,

            "public_key": None,

            "sign_count": 0,

            "transports": [],

            "registered_at": None

        },

        "otp": {

            "verified": False,

            "last_verified_at": None

        },

        "created_at": now,

        "updated_at": now

    }