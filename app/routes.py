from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app 
from werkzeug.security import check_password_hash

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if 'user_id' in session:
        # Obter as últimas movimentações
        response = current_app.supabase.table('movimentacoes').select('*').order('data_saida', desc=True).limit(5).execute()
        movimentacoes = response.data

        # Para cada movimentação, buscar o nome do EPI correspondente
        for mov in movimentacoes:
            if 'epi_id' in mov:
                # Busca o nome do EPI baseado no epi_id
                epi_response = current_app.supabase.table('epis').select('nome').eq('id', mov['epi_id']).execute()
                if epi_response.data:
                    mov['nome_epi'] = epi_response.data[0]['nome']  # Adiciona o nome do EPI à movimentação
                else:
                    mov['nome_epi'] = 'EPI não encontrado'  # Caso o EPI não seja encontrado

            # Convertendo a data de saída para o formato datetime
            if 'data_saida' in mov and mov['data_saida']:
                try:
                    mov['data_saida'] = datetime.strptime(mov['data_saida'], '%Y-%m-%d')
                except ValueError:
                    mov['data_saida'] = None  # Se a data for inválida

        return render_template('index.html', movimentacoes=movimentacoes)
    
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

    # Define as colunas permitidas para ordenação
    colunas_permitidas = ['nome', 'data_validade']
    ordem = request.args.get('ordem', 'nome')  # Coluna de ordenação padrão: 'nome'

    # Valida se a coluna passada está nas permitidas; caso contrário, usa 'nome'
    if ordem not in colunas_permitidas:
        ordem = 'nome'

    # Executa a consulta com a ordenação correta
    response = current_app.supabase.table('epis').select('*').order(ordem, desc=False).execute()
    epis = response.data

    # Converte a data para o formato datetime se presente e válida
    for epi in epis:
        if 'data_validade' in epi and epi['data_validade']:
            try:
                epi['data_validade'] = datetime.strptime(epi['data_validade'], '%Y-%m-%d')
            except ValueError:
                epi['data_validade'] = None  # Se a data estiver inválida

        # Verificação de quantidade baixa
        epi['aviso_estoque'] = epi.get('quantidade', 0) < 3

        # Verificação de validade próxima
        if epi['data_validade']:
            dias_para_vencimento = (epi['data_validade'] - datetime.now()).days
            epi['aviso_validade'] = dias_para_vencimento <= 15
        else:
            epi['aviso_validade'] = False

    return render_template('listar.html', epis=epis, ordem=ordem)

# Função para excluir um item
@main.route('/excluir/<int:item_id>', methods=['POST'])
def excluir(item_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    # Excluir todas as movimentações associadas ao EPI antes de excluí-lo
    current_app.supabase.table('movimentacoes').delete().eq('epi_id', item_id).execute()
    
    # Excluir o EPI
    current_app.supabase.table('epis').delete().eq('id', item_id).execute()
    flash('EPI e movimentações associadas excluídos com sucesso!')
    return redirect(url_for('main.listar'))

# Função para editar um item
@main.route('/editar/<int:item_id>', methods=['GET', 'POST'])
def editar(item_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    # Buscar o item pelo ID
    response = current_app.supabase.table('epis').select('*').eq('id', item_id).execute()
    epi = response.data[0] if response.data else None

    if not epi:
        flash("EPI não encontrado.")
        return redirect(url_for('main.listar'))

    # Atualizar os dados do item quando o formulário for submetido
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        quantidade = request.form['quantidade']
        data_validade = request.form['data_validade']

        # Atualizar o item no banco de dados
        current_app.supabase.table('epis').update({
            'nome': nome,
            'descricao': descricao,
            'quantidade': quantidade,
            'data_validade': data_validade
        }).eq('id', item_id).execute()

        flash("EPI atualizado com sucesso!")
        return redirect(url_for('main.listar'))

    return render_template('editar.html', epi=epi)

@main.route('/controle_saida', methods=['GET', 'POST'])
def controle_saida():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    # Busca a lista de EPIs cadastrados
    response = current_app.supabase.table('epis').select('id, nome, quantidade').execute()
    epis = response.data

    if request.method == 'POST':
        # Obtenha os dados do formulário
        epi_id = request.form['epi_id']
        quantidade_saida = int(request.form['quantidade'])
        solicitante = request.form['solicitante']
        data_saida = request.form['data_saida']

        # Verifica a quantidade disponível
        epi = next((item for item in epis if item['id'] == int(epi_id)), None)
        if not epi or quantidade_saida > epi['quantidade']:
            flash("Quantidade insuficiente em estoque ou EPI não encontrado.")
            return redirect(url_for('main.controle_saida'))

        # Registra a movimentação de saída na tabela `movimentacoes`
        current_app.supabase.table('movimentacoes').insert({
            'epi_id': epi_id,
            'quantidade': quantidade_saida,
            'solicitante': solicitante,
            'data_saida': data_saida
        }).execute()

        # Atualiza a quantidade em estoque do EPI
        nova_quantidade = epi['quantidade'] - quantidade_saida
        current_app.supabase.table('epis').update({'quantidade': nova_quantidade}).eq('id', epi_id).execute()

        flash('Saída registrada com sucesso e estoque atualizado!')
        return redirect(url_for('main.listar'))

    return render_template('controle_saida.html', epis=epis)

@main.route('/relatorio', methods=['GET'])
def relatorio():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    # Pega os filtros dos parâmetros da URL (caso existam)
    solicitante = request.args.get('solicitante', '')
    epi_nome = request.args.get('epi_nome', '')
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')

    # Inicia a consulta
    query = current_app.supabase.table('movimentacoes').select('*')

    # Adiciona filtros conforme os parâmetros recebidos
    if solicitante:
        query = query.ilike('solicitante', f'%{solicitante}%')  # Filtro por nome do solicitante (case insensitive)
    
    if epi_nome:
        # Primeiro, buscar o id dos EPIs com base no nome
        epi_ids_response = current_app.supabase.table('epis').select('id').ilike('nome', f'%{epi_nome}%').execute()
        epi_ids = [epi['id'] for epi in epi_ids_response.data]
        if epi_ids:
            query = query.in_('epi_id', epi_ids)  # Filtra movimentações com os epi_ids encontrados

    if data_inicio:
        query = query.gte('data_saida', data_inicio)  # Filtro por data de saída maior ou igual a data_inicio
    
    if data_fim:
        query = query.lte('data_saida', data_fim)  # Filtro por data de saída menor ou igual a data_fim

    # Ordena pela data de saída
    query = query.order('data_saida', desc=True)

    # Executa a consulta
    response = query.execute()
    movimentacoes = response.data

    # Adiciona o nome do EPI para cada movimentação
    for mov in movimentacoes:
        if 'epi_id' in mov:
            epi_response = current_app.supabase.table('epis').select('nome').eq('id', mov['epi_id']).execute()
            if epi_response.data:
                mov['nome_epi'] = epi_response.data[0]['nome']
            else:
                mov['nome_epi'] = 'EPI não encontrado'

        if 'data_saida' in mov:
            try:
                mov['data_saida'] = datetime.strptime(mov['data_saida'], '%Y-%m-%d')
            except ValueError:
                mov['data_saida'] = None  # Se a data for inválida

    return render_template('relatorio.html', movimentacoes=movimentacoes, solicitante=solicitante, epi_nome=epi_nome, data_inicio=data_inicio, data_fim=data_fim)
