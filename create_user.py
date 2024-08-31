import sqlite3
from werkzeug.security import generate_password_hash

# Conectar ao banco de dados
conn = sqlite3.connect('almoxarifado.db')
c = conn.cursor()

# Usuário e senha a serem criados
username = 'admin'
password = 'senha123'

# Gerar hash da senha
hashed_password = generate_password_hash(password)

# Inserir usuário no banco de dados
c.execute('INSERT INTO usuarios (username, password) VALUES (?, ?)', (username, hashed_password))

conn.commit()
conn.close()

print(f"Usuário '{username}' criado com sucesso!")
