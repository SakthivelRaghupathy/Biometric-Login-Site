from pymongo import MongoClient
from app.core.config import Config

#mongodb connection

client=MongoClient(Config.MONGO_URI)
database=client[Config.DATABASE_NAME]
  
#collection

users_collection=database["users"]
otp_collection=database["otps"]

try:
    client.admin.command("ping")
except Exception as e:
    print("connection failed")
    print(e)
