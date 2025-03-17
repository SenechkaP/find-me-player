from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


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
