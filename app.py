from flask import Flask, render_template, request, redirect, url_for, session, flash
from supabase import create_client, Client
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

# Configurações do Supabase
url = "sua_url_do_supabase"
key = "sua_chave_de_api"
supabase: Client = create_client(url, key)

@app.route('/')
def index():
    if 'user_id' in session:
        response = supabase.table('epis').select('*').execute()
        # epis = conn.execute('SELECT * FROM epis').fetchall()
        epis = response.data
        return render_template('index.html', epis=epis)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # user = conn.execute('SELECT * FROM usuarios WHERE username = ?', (username,)).fetchone()
        response = supabase.table('usuarios').select('*').eq('username', username).execute()
        user = response.data

        if user and check_password_hash(user[0]['password'], password):
            session['user_id'] = user[0]['id']
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

        # conn.execute('INSERT INTO epis (nome, descricao, quantidade, data_validade) VALUES (?, ?, ?, ?)',
        #              (nome, descricao, quantidade, data_validade))

        supabase.table('epis').insert({
            'nome': nome,
            'descricao': descricao,
            'quantidade': quantidade,
            'data_validade': data_validade
        }).execute()

        flash('EPI cadastrado com sucesso!')
        return redirect(url_for('index'))

    return render_template('cadastro.html')

@app.route('/listar')
def listar():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    response = supabase.table('epis').select('*').execute()
    # epis = conn.execute('SELECT * FROM epis').fetchall()
    epis = response.data

    return render_template('listar.html', epis=epis)

if __name__ == '__main__':
    app.run(debug=True)
