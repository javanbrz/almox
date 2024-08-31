from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

def get_db_connection():
    conn = sqlite3.connect('almoxarifado.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    if 'user_id' in session:
        conn = get_db_connection()
        epis = conn.execute('SELECT * FROM epis').fetchall()
        conn.close()
        return render_template('index.html', epis=epis)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM usuarios WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash('Usuário ou senha inválidos')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        quantidade = request.form['quantidade']
        data_validade = request.form['data_validade']

        conn = get_db_connection()
        conn.execute('INSERT INTO epis (nome, descricao, quantidade, data_validade) VALUES (?, ?, ?, ?)',
                     (nome, descricao, quantidade, data_validade))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('cadastro.html')

@app.route('/listar')
def listar():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    epis = conn.execute('SELECT * FROM epis').fetchall()
    conn.close()

    return render_template('listar.html', epis=epis)

if __name__ == '__main__':
    app.run(debug=True)
