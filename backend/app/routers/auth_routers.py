from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.schemas.auth_schema import RegisterRequest
# 1. FIX: Only import the class, do not try to import the method inside it!
from app.services.auth_service import AuthService

auth_router = Blueprint(
    "auth_router",
    __name__,
    url_prefix="/auth"
)

@auth_router.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        validated_data = RegisterRequest(**(data or {}))
        
        # 2. FIX: Call the method directly on the class itself! 
        # (You don't need to do auth_service = AuthService() because it is a @staticmethod)
        response_data = AuthService.register_user(
            username=validated_data.username,
            email=validated_data.email
        )
        
        return jsonify(response_data), 200

    except ValidationError as e:
        return jsonify({
            "success": False, 
            "message": "Invalid request format",
            "details": e.errors()
        }), 400
        
    except ValueError as val_err:
        return jsonify({
            "success": False, 
            "message": str(val_err)
        }), 400
        
    except Exception as e:
        return jsonify({
            "success": False, 
            "message": f"Server error: {str(e)}"
        }), 500