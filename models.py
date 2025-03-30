from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
import bcrypt
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(30), nullable=False)
    email = Column(Text, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    age = Column(Integer, nullable=True)

    def set_password(self, password: str):
        self.password_hash = bcrypt.hashpw(password.encode("UTF-8"), bcrypt.gensalt())

    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode("UTF-8"), self.password_hash.encode("UTF-8"))


class UserRegister(BaseModel):
    name: str = Field(..., min_length=5, max_length=30, pattern="^[A-ZА-Я]?[a-zа-я]{5,30}$")
    email: EmailStr
    password: str = Field(..., min_length=10, pattern="^[a-zA-Z0-9%&*#$!]{10,}$")
    age: Optional[int] = Field(None, ge=14, le=150)

    @field_validator("name")
    def name_must_contain_letters(cls, v: str) -> str:
        if not v.isalpha():
            raise ValueError("Имя должно содержать только буквы")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TeamForm(BaseModel):
    team_name: str
    player1: str
    player2: str
    player3: str
    player4: str
    player5: str

    @field_validator('*')
    def validate_names(cls, value):
        if not value.replace(" ", "").isalpha():
            raise ValueError('Имя должно содержать только буквы')
        return value
