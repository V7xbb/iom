import os, json, hmac, hashlib, base64, time, secrets
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import select
from .database import get_db
from .models import AdminUser

JWT_SECRET = os.getenv('JWT_SECRET_KEY', '')
ISSUER = 'hkrroe-api'

def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 310_000)
    return f'pbkdf2_sha256$310000${_b64(salt)}${_b64(digest)}'

def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, rounds, salt_text, digest_text = encoded.split('$')
        if algorithm != 'pbkdf2_sha256': return False
        salt = base64.urlsafe_b64decode(salt_text + '=' * (-len(salt_text) % 4))
        expected = base64.urlsafe_b64decode(digest_text + '=' * (-len(digest_text) % 4))
        actual = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, int(rounds))
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False

def create_token(user: AdminUser) -> str:
    if len(JWT_SECRET) < 32:
        raise RuntimeError('JWT_SECRET_KEY must be at least 32 characters')
    header = _b64(json.dumps({'alg':'HS256','typ':'JWT'}, separators=(',',':')).encode())
    now = int(time.time())
    payload = _b64(json.dumps({'sub':str(user.id),'username':user.username,'role':user.role,'ver':user.token_version,'iss':ISSUER,'iat':now,'exp':now+60*60*8}, separators=(',',':')).encode())
    body = f'{header}.{payload}'
    signature = _b64(hmac.new(JWT_SECRET.encode(), body.encode(), hashlib.sha256).digest())
    return f'{body}.{signature}'

def get_current_admin(authorization: str | None = Header(default=None), db: Session = Depends(get_db)) -> AdminUser:
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='Authentication required')
    token = authorization[7:]
    try:
        header, payload, signature = token.split('.')
        body = f'{header}.{payload}'
        expected = _b64(hmac.new(JWT_SECRET.encode(), body.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected): raise ValueError('signature')
        data = json.loads(base64.urlsafe_b64decode(payload + '=' * (-len(payload) % 4)))
        if data.get('iss') != ISSUER or int(data.get('exp', 0)) < time.time(): raise ValueError('expired')
        user_id = int(data['sub'])
    except Exception:
        raise HTTPException(status_code=401, detail='Invalid or expired session')
    user = db.get(AdminUser, user_id)
    if not user or not user.is_active or user.role != 'admin' or int(data.get('ver', -1)) != user.token_version:
        raise HTTPException(status_code=403, detail='Admin access denied')
    return user
