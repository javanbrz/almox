import sqlite3

# Conectar ao banco de dados (ou criar se não existir)
conn = sqlite3.connect('almoxarifado.db')
c = conn.cursor()

# Criar tabela de usuários
c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )''')

# Criar tabela de EPIs
c.execute('''CREATE TABLE IF NOT EXISTS epis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT,
                quantidade INTEGER NOT NULL,
                data_validade TEXT
            )''')

conn.commit()
conn.close()
