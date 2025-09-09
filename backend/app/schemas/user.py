import uuid
from pydantic import BaseModel, EmailStr, constr


class UserBase(BaseModel):
    email: EmailStr
    name: str | None = None
    role: str


class UserCreate(BaseModel):
    email: EmailStr
    name: str | None = None
    role: str
    password: constr(min_length=8)


class UserOut(UserBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    token: str