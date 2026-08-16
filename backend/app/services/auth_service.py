import datetime
from typing import Dict, Any

from app.db.mongodb import users_collection

def get_user_by_username(username: str) -> Dict[str, Any]:
    """
    Helper function to fetch a user from the MongoDB database by their username.
    Used across multiple services (Auth, WebAuthn, OTP).
    """
    return users_collection.find_one({"username": username})

class AuthService:

    @staticmethod
    def register_user(username: str, email: str) -> Dict[str, Any]:
        """
        Finalizes the user registration by saving the email and username.
        Handles both UI flow (update existing) and direct API flow (insert new).
        """
        
        # 1. Prevent duplicate emails across different accounts
        existing_email = users_collection.find_one({"email": email})
        if existing_email and existing_email.get("username") != username:
            raise ValueError("This email is already registered to another account.")

        # 2. Check if the user already exists in the database
        # (If they just completed biometric registration, this will be TRUE)
        existing_user = get_user_by_username(username)

        if existing_user:
            # FRONTEND UI FLOW: 
            # The WebAuthn step already created a placeholder document for this username.
            # We just need to UPDATE the document to include their email and finish registration.
            users_collection.update_one(
                {"username": username},
                {
                    "$set": {
                        "email": email,
                        "updated_at": datetime.datetime.utcnow()
                    }
                }
            )
        else:
            # THUNDER CLIENT / POSTMAN FLOW: 
            # The user does not exist at all yet. We need to INSERT a completely new document.
            users_collection.insert_one({
                "username": username,
                "email": email,
                "auth": {
                    "fingerprint_registered": False, 
                    "face_registered": False
                },
                "webauthn": {},
                "created_at": datetime.datetime.utcnow(),
                "updated_at": datetime.datetime.utcnow()
            })

        return {
            "success": True,
            "message": "User profile created successfully"
        }