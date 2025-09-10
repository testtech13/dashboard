from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class PageConfig(BaseModel):
    url: str
    duration_seconds: int
    name: Optional[str] = None


class DashboardConfig(BaseModel):
    pages: List[PageConfig]
    loop: bool = True
    auto_start: bool = False


class StatusResponse(BaseModel):
    is_running: bool
    current_page_index: Optional[int] = None
    current_page: Optional[PageConfig] = None
    time_remaining: Optional[int] = None
    total_pages: int
    last_updated: datetime


class ConfigUpdateRequest(BaseModel):
    config: DashboardConfig


class ControlRequest(BaseModel):
    action: str  # "start", "stop", "pause", "resume"


# Authentication models
class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: bool = False


class UserInDB(User):
    hashed_password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
