from pydantic import BaseModel


class OTPRequest(BaseModel):
    username: str


class OTPResponse(BaseModel):
    success: bool
    message: str


class OTPVerifyRequest(BaseModel):
    username: str
    otp: str


class OTPVerifyResponse(BaseModel):
    success: bool
    message: str