from datetime import datetime, timedelta, timezone

from bson import ObjectId

def create_otp_model(email:str,username:str,otp:str):
    return{
        "id":ObjectId(),
        "username":username,
        "email":email,
        "otp":otp,
        "used":False,
        "created_at":datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(minutes=5)
    }