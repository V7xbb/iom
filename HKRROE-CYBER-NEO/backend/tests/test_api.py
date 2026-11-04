import os
from pathlib import Path

DB_FILE = Path(__file__).resolve().parent / 'test_hkrroe.db'
DB_FILE.unlink(missing_ok=True)
os.environ['DATABASE_URL'] = f"sqlite:///{DB_FILE.as_posix()}"
os.environ['JWT_SECRET_KEY'] = 'test-only-secret-with-at-least-32-chars'
os.environ['ADMIN_USERNAME'] = 'test-admin'
os.environ['ADMIN_PASSWORD'] = 'Test-Only-Strong-Password-123!'
os.environ['CORS_ORIGINS'] = 'http://localhost:3000'

from fastapi.testclient import TestClient
from app.main import app


def test_public_health_and_admin_protection():
    with TestClient(app) as client:
        health = client.get('/api/health')
        assert health.status_code == 200
        assert health.json()['database'] == 'connected'
        assert client.get('/api/admin/overview').status_code == 401


def test_admin_content_and_verification_lifecycle():
    with TestClient(app) as client:
        login = client.post('/api/auth/login', json={
            'username': 'test-admin',
            'password': 'Test-Only-Strong-Password-123!',
        })
        assert login.status_code == 200
        headers = {'Authorization': f"Bearer {login.json()['access_token']}"}

        project = {
            'title': 'API project test', 'description': 'Test description',
            'category': 'Development', 'tech_stack': 'Python', 'image_url': '',
            'demo_url': '', 'source_url': '', 'status': 'completed',
            'featured': True, 'published': True,
        }
        assert client.post('/api/admin/projects', json=project, headers=headers).status_code == 201
        assert len(client.get('/api/projects').json()) == 1

        article = {'title': 'API news test', 'body': 'Published test', 'image_url': '', 'published': True}
        assert client.post('/api/admin/news', json=article, headers=headers).status_code == 201
        assert len(client.get('/api/news').json()) == 1

        created = client.post('/api/admin/verifications', headers=headers, json={
            'subject': 'HKRROE test identity', 'details': 'Internal site record'
        })
        assert created.status_code == 201
        record = created.json()
        changed = client.patch(f"/api/admin/verifications/{record['id']}", headers=headers, json={'status': 'approved'})
        assert changed.status_code == 200
        assert client.get(f"/api/verified/{record['public_id']}").json()['status'] == 'approved'

        settings = client.put('/api/admin/settings', headers=headers, json={
            'socials': {'telegram': 'https://t.me/hkrroe'}, 'profile': {'name': 'HKRROE'}
        })
        assert settings.status_code == 200
        assert client.get('/api/settings').json()['socials']['telegram'] == 'https://t.me/hkrroe'
