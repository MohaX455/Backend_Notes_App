from pydantic import BaseModel, EmailStr, Field, field_validator
import re


# =========================
# BASE RESPONSE
# =========================

class MessageResponse(BaseModel):
    message: str


# =========================
# USER RESPONSE
# =========================

class AuthUserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr


# =========================
# TOKEN RESPONSE
# =========================

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# =========================
# REGISTER
# =========================

class RegisterRequest(BaseModel):

    username: str = Field(
        min_length=3,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_]+$"
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str):

        forbidden = {
            "admin",
            "root",
            "support",
            "system"
        }

        if value.lower() in forbidden:
            raise ValueError("Username not allowed")

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):

        # uppercase
        if not re.search(r"[A-Z]", value):
            raise ValueError(
                "Password must contain uppercase letter"
            )

        # lowercase
        if not re.search(r"[a-z]", value):
            raise ValueError(
                "Password must contain lowercase letter"
            )

        # number
        if not re.search(r"\d", value):
            raise ValueError(
                "Password must contain number"
            )

        return value


class RegisterResponse(BaseModel):
    message: str
    user: AuthUserResponse


# =========================
# LOGIN
# =========================

class LoginRequest(BaseModel):

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128
    )


class LoginResponse(BaseModel):
    message: str
    token: TokenResponse
    user: AuthUserResponse


# =========================
# REFRESH
# =========================

class RefreshResponse(BaseModel):
    token: TokenResponse


# =========================
# LOGOUT
# =========================

class LogoutResponse(MessageResponse):
    pass