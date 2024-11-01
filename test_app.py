import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index(client):
    """Testa a rota index."""
    response = client.get('/')
    assert response.status_code == 302  # Espera redirecionamento

def test_login(client):
    """Testa a rota de login."""
    response = client.get('/login')
    assert response.status_code == 200  # Espera status 200
