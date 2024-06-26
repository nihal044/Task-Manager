from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str
    role: str

class User(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class TaskCreate(BaseModel):
    title: str
    description: str
    due_date: datetime

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    completed: bool | None = None

class Task(BaseModel):
    id: int
    title: str
    description: str
    due_date: datetime
    completed: bool
    user_id: int

    class Config:
        from_attributes = True
