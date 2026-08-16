from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr


class RegisterResponse(BaseModel):
    success: bool
    message: str


class LoginRequest(BaseModel):
    username: str


class LoginResponse(BaseModel):
    success: bool
    message: str


class LogoutResponse(BaseModel):
    success: bool
    message: str