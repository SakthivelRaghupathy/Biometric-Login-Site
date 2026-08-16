from flask_cors import CORS

from app.db.mongodb import client
from flask import Flask
from app.routers.auth_routers import auth_router
from app.routers.otp_router import otp_router
from app.routers.webauthn_router import webauthn_router
app=Flask(__name__)
CORS(app)
app.register_blueprint(auth_router)
app.register_blueprint(otp_router)
app.register_blueprint(webauthn_router)
print(app.url_map)
if __name__=="__main__":
    app.run(debug=True)
