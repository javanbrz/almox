from supabase import create_client, Client
from werkzeug.security import generate_password_hash

# Configurações do Supabase
url = "sua_url_do_supabase"
key = "sua_chave_de_api"
supabase: Client = create_client(url, key)

# Usuário e senha a serem criados
username = 'admin'
password = 'senha123'

# Gerar hash da senha
hashed_password = generate_password_hash(password)

# Inserir usuário no banco de dados
response = supabase.table('usuarios').insert({
    'username': username,
    'password': hashed_password
}).execute()

if response.status_code == 201:
    print(f"Usuário '{username}' criado com sucesso!")
else:
    print("Erro ao criar usuário:", response.error_message)
