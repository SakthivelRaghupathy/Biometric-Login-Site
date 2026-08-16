import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI")
    DATABASE_NAME = os.getenv("DATABASE_NAME")
    SECRET_KEY = os.getenv("SECRET_KEY")
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
    EMAIL_HOST = os.getenv("EMAIL_HOST")   
    EMAIL_PORT = int(os.getenv("EMAIL_PORT"))
    OTP_EXPIRY_SECONDS = int(os.getenv("OTP_EXPIRY_SECONDS", 300))
    RP_ID = os.environ.get("WEBAUTHN_RP_ID")
    RP_NAME = os.environ.get("WEBAUTHN_RP_NAME")
    EXPECTED_ORIGIN = os.environ.get("WEBAUTHN_EXPECTED_ORIGIN")

