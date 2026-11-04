import os, time, uuid, json, hashlib, secrets
from datetime import datetime, timezone
from collections import defaultdict, deque
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from sqlalchemy import select, desc, func, text
from sqlalchemy.orm import Session
from .database import Base, engine, get_db, SessionLocal
from .models import AdminUser, Project, News, Verification, Activity, SiteSetting, Visit
from .schemas import LoginIn, PasswordChange, ProjectIn, ProjectOut, NewsIn, NewsOut, VerificationIn, VerificationOut, VerificationStatus, SettingsIn
from .security import hash_password, verify_password, create_token, get_current_admin

APP_STARTED = time.time()
LOGIN_ATTEMPTS: dict[str, deque] = defaultdict(deque)
VERIFY_ATTEMPTS: dict[str, deque] = defaultdict(deque)
DEFAULT_SOCIALS = {
    'telegram':'https://t.me/hkrroe',
    'whatsapp':'https://wa.me/201201165541',
    'instagram':'https://instagram.com/hkrroe',
    'tiktok':'https://www.tiktok.com/@hkrroe',
    'youtube':'https://www.youtube.com/@hkrroe',
    'discord':'https://discord.com/app'
}
app = FastAPI(title='HKRROE API', version='2.0.0', description='Admin-managed digital identity and portfolio API')
origins = [x.strip() for x in os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',') if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=['GET','POST','PUT','PATCH','DELETE','OPTIONS'], allow_headers=['Authorization','Content-Type'])

@app.middleware('http')
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    response.headers['Cache-Control'] = 'no-store' if request.url.path.startswith('/api/admin') or request.url.path == '/api/auth/login' else 'public, max-age=30'
    return response

def log_activity(db: Session, message: str):
    db.add(Activity(message=message[:240]))
    db.flush()

def seed_defaults(db: Session):
    if not db.scalar(select(SiteSetting).where(SiteSetting.key == 'socials')):
        db.add(SiteSetting(key='socials', value=json.dumps(DEFAULT_SOCIALS)))
    if not db.scalar(select(SiteSetting).where(SiteSetting.key == 'profile')):
        db.add(SiteSetting(key='profile', value=json.dumps({'name':'HKRROE','handle':'@hkrroe','location':'Assiut, Egypt','tagline':'Building Smart Digital Experiences.'})))
    username, password = os.getenv('ADMIN_USERNAME','').strip(), os.getenv('ADMIN_PASSWORD','')
    if username and password and not db.scalar(select(AdminUser).where(AdminUser.username == username)):
        if len(password) < 12:
            raise RuntimeError('ADMIN_PASSWORD must be at least 12 characters')
        db.add(AdminUser(username=username, password_hash=hash_password(password), role='admin'))
        log_activity(db, 'Admin account initialized')
    db.commit()

@app.on_event('startup')
def startup():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_defaults(db)

def admin_dep(user: AdminUser = Depends(get_current_admin)):
    return user

@app.get('/api/health')
def health(db: Session = Depends(get_db)):
    started = time.perf_counter()
    try:
        db.execute(text('SELECT 1'))
        return {'status':'ok','service':'HKRROE API','database':'connected','db_check_ms':round((time.perf_counter()-started)*1000,2),'uptime_seconds':int(time.time()-APP_STARTED)}
    except Exception:
        return JSONResponse(status_code=503, content={'status':'degraded','service':'HKRROE API','database':'disconnected'})

@app.post('/api/auth/login')
def login(payload: LoginIn, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host if request.client else 'unknown'
    now = time.time(); attempts = LOGIN_ATTEMPTS[ip]
    while attempts and now - attempts[0] > 60: attempts.popleft()
    if len(attempts) >= 5: raise HTTPException(429, 'محاولات كتير. جرّب بعد دقيقة.')
    attempts.append(now)
    user = db.scalar(select(AdminUser).where(AdminUser.username == payload.username))
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, 'اسم المستخدم أو كلمة المرور غير صحيحة')
    attempts.clear()
    return {'access_token':create_token(user),'token_type':'bearer','expires_in':28800,'username':user.username}

@app.get('/api/auth/me')
def auth_me(user: AdminUser = Depends(admin_dep)):
    return {'id':user.id,'username':user.username,'role':user.role}

@app.post('/api/auth/change-password')
def change_password(payload: PasswordChange, user: AdminUser = Depends(admin_dep), db: Session = Depends(get_db)):
    if not verify_password(payload.current_password, user.password_hash): raise HTTPException(400, 'كلمة المرور الحالية غير صحيحة')
    user.password_hash = hash_password(payload.new_password)
    user.token_version += 1
    log_activity(db, 'Admin password changed'); db.commit()
    return {'changed':True,'message':'تم تغيير كلمة المرور. سجّل دخولك تاني.'}

@app.get('/api/stats')
def stats(db: Session = Depends(get_db)):
    project_count = db.scalar(select(func.count(Project.id)).where(Project.published.is_(True))) or 0
    today = datetime.now(timezone.utc).date().isoformat()
    visit_count = db.scalar(select(func.count(Visit.id)).where(Visit.visit_day == today)) or 0
    return {'projects':project_count,'visits':visit_count,'uptime_seconds':int(time.time()-APP_STARTED)}

@app.post('/api/visits', status_code=204)
def record_visit(request: Request, db: Session = Depends(get_db)):
    ip = request.client.host if request.client else 'unknown'
    day = datetime.now(timezone.utc).date().isoformat()
    salt = os.getenv('VISITOR_HASH_SECRET') or os.getenv('JWT_SECRET_KEY','hkrroe-local-secret')
    key = hashlib.sha256(f'{ip}|{day}|{salt}'.encode()).hexdigest()
    exists = db.scalar(select(Visit.id).where(Visit.visitor_key == key, Visit.visit_day == day))
    if not exists:
        db.add(Visit(visitor_key=key, visit_day=day)); db.commit()
    return Response(status_code=204)

@app.get('/api/projects', response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return db.scalars(select(Project).where(Project.published.is_(True)).order_by(desc(Project.featured), desc(Project.created_at))).all()

@app.get('/api/news', response_model=list[NewsOut])
def list_news(db: Session = Depends(get_db)):
    return db.scalars(select(News).where(News.published.is_(True)).order_by(desc(News.created_at)).limit(20)).all()

@app.get('/api/activity')
def activity(db: Session = Depends(get_db)):
    rows = db.scalars(select(Activity).order_by(desc(Activity.created_at)).limit(10)).all()
    return [{'id':x.id,'message':x.message,'created_at':x.created_at.isoformat()} for x in rows]

@app.get('/api/settings')
def public_settings(db: Session = Depends(get_db)):
    rows = {x.key:x.value for x in db.scalars(select(SiteSetting)).all()}
    try: socials = json.loads(rows.get('socials','{}'))
    except ValueError: socials = DEFAULT_SOCIALS
    try: profile = json.loads(rows.get('profile','{}'))
    except ValueError: profile = {}
    return {'socials':socials,'profile':profile}

@app.post('/api/verified', response_model=VerificationOut, status_code=201)
def request_verification(payload: VerificationIn, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host if request.client else 'unknown'
    now = time.time(); attempts = VERIFY_ATTEMPTS[ip]
    while attempts and now - attempts[0] > 3600: attempts.popleft()
    if len(attempts) >= 5: raise HTTPException(429, 'تم الوصول للحد المسموح من الطلبات. حاول لاحقًا.')
    attempts.append(now)
    item = Verification(public_id='HKR-' + uuid.uuid4().hex[:10].upper(), subject=payload.subject, details=payload.details, status='pending')
    db.add(item); log_activity(db, 'New verification request received'); db.commit(); db.refresh(item)
    return item

@app.get('/api/verified/{public_id}', response_model=VerificationOut)
def check_verification(public_id: str, db: Session = Depends(get_db)):
    item = db.scalar(select(Verification).where(Verification.public_id == public_id.upper()))
    if not item: raise HTTPException(404, 'Verification record not found')
    return item

# Admin-only content management
@app.get('/api/admin/overview')
def admin_overview(user: AdminUser = Depends(admin_dep), db: Session = Depends(get_db)):
    return {'projects':db.scalar(select(func.count(Project.id))) or 0,'news':db.scalar(select(func.count(News.id))) or 0,'verifications':db.scalar(select(func.count(Verification.id))) or 0,'visits':db.scalar(select(func.count(Visit.id))) or 0}

@app.get('/api/admin/projects', response_model=list[ProjectOut])
def admin_projects(user: AdminUser = Depends(admin_dep), db: Session = Depends(get_db)):
    return db.scalars(select(Project).order_by(desc(Project.created_at))).all()

@app.post('/api/admin/projects', response_model=ProjectOut, status_code=201)
def create_project(payload: ProjectIn, user: AdminUser = Depends(admin_dep), db: Session = Depends(get_db)):
    item = Project(**payload.model_dump()); db.add(item); log_activity(db, f'Project created: {item.title}'); db.commit(); db.refresh(item); return item

@app.put('/api/admin/projects/{item_id}', response_model=ProjectOut)
def update_project(item_id: int, payload: ProjectIn, user: AdminUser = Depends(admin_dep), db: Session = Depends(get_db)):
    item = db.get(Project, item_id)
    if not item: raise HTTPException(404, 'Project not found')
    for key, value in payload.model_dump().items(): setattr(item, key, value)
    log_activity(db, f'Project updated: {item.title}'); db.commit(); db.refresh(item); return item

@app.delete('/api/admin/projects/{item_id}')
def delete_project(item_id: int, user: AdminUser = Depends(admin_dep), db: Session = Depends(get_db)):
    item = db.get(Project, item_id)
    if not item: raise HTTPException(404, 'Project not found')
    title = item.title; db.delete(item); log_activity(db, f'Project deleted: {title}'); db.commit(); return {'deleted':True}

@app.get('/api/admin/news', response_model=list[NewsOut])
def admin_news(user: AdminUser = Depends(admin_dep), db: Session = Depends(get_db)):
    return db.scalars(select(News).order_by(desc(News.created_at))).all()

@app.post('/api/admin/news', response_model=NewsOut, status_code=201)
def create_news(payload: NewsIn, user: AdminUser = Depends(admin_dep), db: Session = Depends(get_db)):
    item = News(**payload.model_dump()); db.add(item); log_activity(db, f'News published: {item.title}'); db.commit(); db.refresh(item); return item

@app.put('/api/admin/news/{item_id}', response_model=NewsOut)
def update_news(item_id: int, payload: NewsIn, user: AdminUser = Depends(admin_dep), db: Session = Depends(get_db)):
    item = db.get(News, item_id)
    if not item: raise HTTPException(404, 'News not found')
    for key, value in payload.model_dump().items(): setattr(item, key, value)
    log_activity(db, f'News updated: {item.title}'); db.commit(); db.refresh(item); return item

@app.delete('/api/admin/news/{item_id}')
def delete_news(item_id: int, user: AdminUser = Depends(admin_dep), db: Session = Depends(get_db)):
    item = db.get(News, item_id)
    if not item: raise HTTPException(404, 'News not found')
    title = item.title; db.delete(item); log_activity(db, f'News deleted: {title}'); db.commit(); return {'deleted':True}

@app.post('/api/admin/verifications', response_model=VerificationOut, status_code=201)
def admin_create_verification(payload: VerificationIn, user: AdminUser = Depends(admin_dep), db: Session = Depends(get_db)):
    item = Verification(public_id='HKR-' + uuid.uuid4().hex[:10].upper(), subject=payload.subject, details=payload.details, status='pending')
    db.add(item); log_activity(db, f'Verification record created: {item.subject}'); db.commit(); db.refresh(item); return item

@app.get('/api/admin/verifications', response_model=list[VerificationOut])
def admin_verifications(user: AdminUser = Depends(admin_dep), db: Session = Depends(get_db)):
    return db.scalars(select(Verification).order_by(desc(Verification.created_at))).all()

@app.patch('/api/admin/verifications/{item_id}', response_model=VerificationOut)
def set_verification_status(item_id: int, payload: VerificationStatus, user: AdminUser = Depends(admin_dep), db: Session = Depends(get_db)):
    item = db.get(Verification, item_id)
    if not item: raise HTTPException(404, 'Verification not found')
    item.status = payload.status
    log_activity(db, f'Verification {item.public_id}: {payload.status}'); db.commit(); db.refresh(item); return item

@app.put('/api/admin/settings')
def update_settings(payload: SettingsIn, user: AdminUser = Depends(admin_dep), db: Session = Depends(get_db)):
    values = {'socials':json.dumps(payload.socials, ensure_ascii=False),'profile':json.dumps(payload.profile, ensure_ascii=False)}
    for key, value in values.items():
        row = db.scalar(select(SiteSetting).where(SiteSetting.key == key))
        if row: row.value = value
        else: db.add(SiteSetting(key=key, value=value))
    log_activity(db, 'Site settings updated'); db.commit(); return {'saved':True}

@app.get('/api/admin/activity')
def admin_activity(user: AdminUser = Depends(admin_dep), db: Session = Depends(get_db)):
    return [{'id':x.id,'message':x.message,'created_at':x.created_at.isoformat()} for x in db.scalars(select(Activity).order_by(desc(Activity.created_at)).limit(100)).all()]
