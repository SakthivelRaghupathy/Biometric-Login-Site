import random
from datetime import datetime, timedelta

from app.db.mongodb import otp_collection
from app.core.config import Config

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# ----------------------------------------
# Generate OTP
# ----------------------------------------

def create_otp():

    return str(random.randint(100000, 999999))


# ----------------------------------------
# Store OTP
# ----------------------------------------

def store_otp(email: str, otp: str):

    otp_collection.delete_many({"email": email})

    otp_collection.insert_one({

        "email": email,

        "otp": otp,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(seconds=Config.OTP_EXPIRY_SECONDS)

        

    })


# ----------------------------------------
# Send OTP Email
# ----------------------------------------

def send_otp_email(
    email: str,
    username: str,
    otp: str
):

    try:

        message = MIMEMultipart()

        message["From"] = Config.SENDER_EMAIL
        message["To"] = email
        message["Subject"] = "BioSecure OTP Verification"

        body = f"""
Hello {username},

Your BioSecure verification code is:

{otp}

This OTP will expire in 5 minutes.

If you did not request this login, please ignore this email.

Regards,
BioSecure Team
"""

        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(
            Config.EMAIL_HOST,
            Config.EMAIL_PORT
        ) as server:

            server.starttls()

            server.login(
                Config.SENDER_EMAIL,
                Config.SENDER_PASSWORD
            )

            server.sendmail(
                Config.SENDER_EMAIL,
                email,
                message.as_string()
            )

        return True

    except Exception as e:

        print("Email Error:", e)

        return False


# ----------------------------------------
# Verify OTP
# ----------------------------------------

def verify_otp(
    email: str,
    otp: str
):

    record = otp_collection.find_one({

        "email": email,

        "otp": otp

    })

    if record is None:

        return False
    if datetime.utcnow() > record["expires_at"]:
        
        otp_collection.delete_one({

            "_id": record["_id"]

        })

        return False

    otp_collection.delete_one({

        "_id": record["_id"]

    })

    return True