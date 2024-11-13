from flask.testing import FlaskClient
import pytest
from app import create_app
from datetime import datetime, timedelta
from flask import current_app 

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_redirect(client: FlaskClient):
    """Testa o redirecionamento da rota index quando não logado."""
    response = client.get('/')
    assert response.status_code == 302  # Espera redirecionamento para login

def test_login(client: FlaskClient):
    """Testa a rota de login."""
    response = client.get('/login')
    assert response.status_code == 200  # Espera status 200

def test_cadastro_epi(client: FlaskClient):
    """Testa o cadastro de um novo EPI."""
    # Simula um usuário logado
    with client.session_transaction() as session:
        session['user_id'] = 1  # Define um ID de usuário fictício para o teste

    response = client.post('/cadastro', data={
        'nome': 'Capacete',
        'descricao': 'Capacete de segurança',
        'quantidade': 10,
        'data_validade': '2024-11-15'
    })
    assert response.status_code == 302  # Espera redirecionamento após cadastro

def test_listar_epis(client: FlaskClient):
    """Testa a listagem de EPIs e verifica avisos de estoque baixo e validade próxima."""
    # Simula um usuário logado
    with client.session_transaction() as session:
        session['user_id'] = 1
    
    response = client.get('/listar')
    assert response.status_code == 200

    # Verifica se a resposta contém os avisos corretos
    html = response.get_data(as_text=True)
    assert 'Estoque Baixo!' in html or 'Próximo do Vencimento!' in html

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_editar_epi(client):
    """Testa a edição de um EPI."""
    # Simula um usuário logado
    with client.session_transaction() as session:
        session['user_id'] = 1

    with current_app.app_context():
        # Obter o último ID cadastrado na tabela 'epis'
        response = current_app.supabase.table('epis').select('id').order('id', desc=True).limit(1).execute()
        ultimo_id = response.data[0]['id'] if response.data else None

    if ultimo_id is not None:
        response = client.post(f'/editar/{ultimo_id}', data={
            'nome': 'Capacete de segurança (up)',
            'descricao': 'Lote 2025',
            'quantidade': 8,
            'data_validade': '2024-11-25'
        })
        assert response.status_code == 302  # Espera redirecionamento após edição
    else:
        assert False, "Nenhum EPI encontrado para editar"


def test_excluir_epi(client):
    """Testa a exclusão de um EPI."""
    # Simula um usuário logado
    with client.session_transaction() as session:
        session['user_id'] = 1

    with current_app.app_context():
        # Obter o último ID cadastrado na tabela 'epis'
        response = current_app.supabase.table('epis').select('id').order('id', desc=True).limit(1).execute()
        ultimo_id = response.data[0]['id'] if response.data else None

    if ultimo_id is not None:
        response = client.post(f'/excluir/{ultimo_id}')
        assert response.status_code == 302  # Espera redirecionamento após exclusão
    else:
        assert False, "Nenhum EPI encontrado para excluir"

def test_movimentacao_saida(client: FlaskClient):
    """Testa a criação de uma movimentação de saída e a atualização de quantidade no estoque."""
    # Simula um usuário logado
    with client.session_transaction() as session:
        session['user_id'] = 1

    # Primeiro cadastra um EPI para a movimentação
    client.post('/cadastro', data={
        'nome': 'Capacete',
        'descricao': 'Capacete de segurança',
        'quantidade': 10,
        'data_validade': '2025-11-12'
    })

    # Obter o último ID cadastrado na tabela 'epis'
    response = current_app.supabase.table('epis').select('id').order('id', desc=True).limit(1).execute()

    # Verifica se a resposta contém dados e armazena o último ID
    ultimo_id = response.data[0]['id'] if response.data else None

    # Em seguida, cria uma movimentação de saída
    response = client.post('/controle_saida', data={
        'epi_id': ultimo_id,  # Pega o último ID do EPI recém-criado
        'quantidade': 3,
        'solicitante': 'João da Silva',
        'data_saida': '2024-11-12'
    })
    assert response.status_code == 302  # Espera redirecionamento após movimentação
    
    # Verifica se a quantidade foi atualizada corretamente
    response = client.get('/listar')