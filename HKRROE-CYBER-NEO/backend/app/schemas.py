from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Any
from datetime import datetime

class LoginIn(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=200)

class PasswordChange(BaseModel):
    current_password: str = Field(min_length=1, max_length=200)
    new_password: str = Field(min_length=12, max_length=200)

def _check_optional_url(value: str) -> str:
    if value and not (value.startswith('https://') or value.startswith('http://')):
        raise ValueError('URL must start with http:// or https://')
    return value

class ProjectIn(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    description: str = Field(default='', max_length=3000)
    category: str = Field(default='Development', max_length=60)
    tech_stack: str = Field(default='', max_length=300)
    image_url: str = Field(default='', max_length=500)
    demo_url: str = Field(default='', max_length=500)
    source_url: str = Field(default='', max_length=500)
    status: str = Field(default='in-progress', max_length=30)
    featured: bool = False
    published: bool = True

    @field_validator('image_url','demo_url','source_url')
    @classmethod
    def validate_project_urls(cls, value): return _check_optional_url(value)

class ProjectOut(ProjectIn):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class NewsIn(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    body: str = Field(default='', max_length=5000)
    image_url: str = Field(default='', max_length=500)
    published: bool = True

    @field_validator('image_url')
    @classmethod
    def validate_news_image(cls, value): return _check_optional_url(value)

class NewsOut(NewsIn):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class VerificationIn(BaseModel):
    subject: str = Field(min_length=2, max_length=120)
    details: str = Field(default='', max_length=3000)

class VerificationOut(BaseModel):
    id: int
    created_at: datetime
    public_id: str
    subject: str
    status: str
    details: str
    model_config = ConfigDict(from_attributes=True)

class VerificationStatus(BaseModel):
    status: str = Field(pattern='^(approved|revoked|pending)$')

class SettingsIn(BaseModel):
    socials: dict[str, str]
    profile: dict[str, str] = {}

    @field_validator('socials')
    @classmethod
    def validate_socials(cls, value):
        allowed = {'telegram','whatsapp','instagram','tiktok','youtube','discord'}
        if set(value) - allowed: raise ValueError('Unknown social platform')
        for key, url in value.items():
            if len(url) > 500: raise ValueError(f'{key} URL is too long')
            if url and not (url.startswith('https://') or url.startswith('http://')): raise ValueError(f'{key} must be an http(s) URL')
        return value
