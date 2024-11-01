from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app 
from werkzeug.security import check_password_hash

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if 'user_id' in session:
        response = current_app.supabase.table('epis').select('*').execute()
        # epis = conn.execute('SELECT * FROM epis').fetchall()
        epis = response.data
        for epi in epis:
        # Supondo que a data esteja no formato 'YYYY-MM-DD'
            epi['data_validade'] = datetime.strptime(epi['data_validade'], '%Y-%m-%d')

        return render_template('index.html', epis=epis)
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # user = conn.execute('SELECT * FROM usuarios WHERE username = ?', (username,)).fetchone()
        response = current_app.supabase.table('usuarios').select('*').eq('username', username).execute()
        user = response.data

        if user and check_password_hash(user[0]['password'], password):
            session['user_id'] = user[0]['id']
            return redirect(url_for('main.index'))

        flash('Usuário ou senha inválidos')
    return render_template('login.html')

@main.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main.login'))

@main.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        quantidade = request.form['quantidade']
        data_validade = request.form['data_validade']

        # conn.execute('INSERT INTO epis (nome, descricao, quantidade, data_validade) VALUES (?, ?, ?, ?)',
        #              (nome, descricao, quantidade, data_validade))

        current_app.supabase.table('epis').insert({
            'nome': nome,
            'descricao': descricao,
            'quantidade': quantidade,
            'data_validade': data_validade
        }).execute()

        flash('EPI cadastrado com sucesso!')
        return redirect(url_for('main.index'))

    return render_template('cadastro.html')

@main.route('/listar')
def listar():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    response = current_app.supabase.table('epis').select('*').execute()
    # epis = conn.execute('SELECT * FROM epis').fetchall()
    epis = response.data
    
    for epi in epis:
        # Supondo que a data esteja no formato 'YYYY-MM-DD'
        epi['data_validade'] = datetime.strptime(epi['data_validade'], '%Y-%m-%d')


    return render_template('listar.html', epis=epis)
