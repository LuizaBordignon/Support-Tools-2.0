from flask import Flask, render_template, request, url_for, jsonify, send_file, Response, stream_with_context
from ftplib import FTP, error_perm
import uuid, sqlite3

# =========================
# BANCO DE TOKENS
# =========================

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS atendimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT UNIQUE,
            tipo TEXT,              -- upload ou download
            caminho TEXT,
            arquivo TEXT,           -- nome do arquivo (só para download)
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

def salvar_token(token, tipo, caminho, arquivo=None):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO atendimentos (token, tipo, caminho, arquivo)
        VALUES (?, ?, ?, ?)
    """, (token, tipo, caminho, arquivo))

    conn.commit()
    conn.close()


def buscar_token(token):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tipo, caminho, arquivo
        FROM atendimentos
        WHERE token = ?
    """, (token,))

    resultado = cursor.fetchone()
    conn.close()

    return resultado


app = Flask(__name__)
init_db()

# =========================
# LISTAGENS FTP
# =========================

def listar_cliente():
    ftp = FTP('ftp.dominiosistemas.com.br')
    ftp.login(user='suportesc', passwd='pmn7755')

    ftp.cwd('/') #raiz
    itens = []
    ftp.dir(itens.append) 
    ftp.quit()

    unidades = []
    for linha in itens:
        if linha.startswith('d'): 
            unidades.append(linha.split()[-1]) 

    return unidades


def listar_diretorios_ftp(tipo):
    if not tipo: return []
    try:
        ftp = FTP('ftp.dominiosistemas.com.br')
        ftp.login(user='suportesc', passwd='pmn7755')

        ftp.cwd(f'/{tipo}')
        itens = []
        ftp.dir(itens.append)
        ftp.quit()

        diretorios = []
        for linha in itens:
            if linha.startswith('d'):
                nome = linha.split()[-1]
                if nome not in ('.', '..'):
                    diretorios.append(nome)
        return diretorios
    except:
        return []

# =========================
# FUNÇÕES DE VERIFICAÇÃO
# =========================

def caminho_existe_ftp(caminho):
    ftp = FTP('ftp.dominiosistemas.com.br')
    try:
        ftp.login(user='suportesc', passwd='pmn7755')
        ftp.cwd(caminho)
        return True
    except error_perm:
        return False
    finally:
        try: ftp.quit()
        except: pass


def arquivo_existe_ftp(caminho, nome_arquivo):
    ftp = FTP('ftp.dominiosistemas.com.br')
    try:
        ftp.login(user='suportesc', passwd='pmn7755')
        ftp.set_pasv(True)
        ftp.voidcmd('TYPE I')
        ftp.cwd(caminho)

        try:
            ftp.size(nome_arquivo)
            return True
        except error_perm:
            return False

    finally:
        try:
            ftp.quit()
        except:
            pass

# =========================
# ROTAS DE PÁGINAS
# =========================

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/listar_diretorios/<tipo>')
def listar_por_tipo(tipo):
    try:
        diretorios = listar_diretorios_ftp(tipo)
        return jsonify(diretorios)
    except:
        return jsonify([])
    
@app.route('/verificar_pasta', methods=['POST'])
def verificar_pasta():
    caminho = request.json.get('caminho')
    if not caminho:
        return jsonify({'existe': False})
    existe = caminho_existe_ftp(caminho)
    return jsonify({'existe': existe})

@app.route('/criar_pasta', methods=['POST'])
def criar_pasta():
    caminho = request.form.get('caminho')
    if not caminho:
        return jsonify({'sucesso': False, 'erro': 'Caminho não informado'})

    ftp = FTP('ftp.dominiosistemas.com.br')
    try:
        ftp.login(user='suportesc', passwd='pmn7755')
        ftp.cwd('/') 
        partes = caminho.strip('/').split('/')

        for pasta in partes:
            try:
                ftp.cwd(pasta)
            except error_perm:
                ftp.mkd(pasta)
                ftp.cwd(pasta)

        return jsonify({'sucesso': True})
    except error_perm as e:
        return jsonify({'sucesso': False, 'erro': str(e)})
    finally:
        try: ftp.quit()
        except: pass


@app.route("/envio")
def envio():
    unidades = listar_cliente() 
    return render_template('enviar.html', unidades=unidades, diretorios=[])

@app.route("/baixar")
def baixar():
    unidades = listar_cliente()
    return render_template('baixar.html', unidades=unidades, diretorios=[])


# =========================
# GERAÇÃO DE LINK (ENVIO)
# =========================

@app.route('/gerar_link', methods=['POST'])
def gerar_link():
    tipo = request.form.get('tipo')
    unidade = request.form.get('unidade')
    codigo = request.form.get('codigo')
    subpastas = request.form.getlist('subpasta[]')

    if not tipo or not unidade or not codigo:
        return "Campos obrigatórios não preenchidos", 400

    caminho = f"/{tipo}/{unidade}/{codigo}"
    for subpasta in subpastas:
        if subpasta.strip():
            caminho += f"/{subpasta.strip()}"

    # Recarrega a lista de diretórios se der erro, para não limpar o form
    if not caminho_existe_ftp(caminho):
        unidades = listar_cliente()
        diretorios = listar_diretorios_ftp(tipo) 
        
        return render_template(
            'enviar.html',
            unidades=unidades,
            diretorios=diretorios,
            erro_pasta="A pasta informada não existe. Deseja criar?",
            caminho=caminho,
            form_data=request.form 
        )

    token = str(uuid.uuid4())

    salvar_token(
        token=token,
        tipo="upload",
        caminho=caminho
    )

    link_cliente = url_for('upload_cliente', token=token, _external=True)

    diretorios = listar_diretorios_ftp(tipo)
    unidades = listar_cliente()

    return render_template(
        'enviar.html',
        diretorios=diretorios,
        unidades=unidades,
        link=link_cliente,
        form_data=request.form
    )


# =========================
# GERAÇÃO DE LINK (DOWNLOAD)
# =========================

@app.route('/gerar_link_download', methods=['POST'])
def gerar_link_download():
    tipo = request.form.get('tipo')
    unidade = request.form.get('unidade')
    codigo = request.form.get('codigo')
    nome_arquivo = request.form.get('nome_arquivo')
    subpastas = request.form.getlist('subpasta[]')

    if not tipo or not unidade or not codigo or not nome_arquivo:
        return "Campos obrigatórios não preenchidos", 400

    caminho = f"/{tipo}/{unidade}/{codigo}"
    for subpasta in subpastas:
        if subpasta.strip():
            caminho += f"/{subpasta.strip()}"

    # ERRO DE PASTA
    if not caminho_existe_ftp(caminho):
        unidades = listar_cliente()
        diretorios = listar_diretorios_ftp(tipo)
        
        return render_template(
            'baixar.html',
            diretorios=diretorios,
            unidades=unidades,
            erro_pasta="A pasta informada não existe. Deseja criar?",
            caminho=caminho,
            form_data=request.form
        )

    # ERRO DE ARQUIVO
    if not arquivo_existe_ftp(caminho, nome_arquivo):
        unidades = listar_cliente()
        diretorios = listar_diretorios_ftp(tipo)
        
        return render_template(
            'baixar.html',
            diretorios=diretorios,
            unidades=unidades,
            erro_arquivo="O arquivo informado não existe nesta pasta.",
            form_data=request.form
        )

    token = str(uuid.uuid4())

    salvar_token(
        token=token,
        tipo="download",
        caminho=caminho,
        arquivo=nome_arquivo
    )

    link_cliente = url_for(
        'pagina_download_cliente',
        token=token,
        _external=True
    )

    diretorios = listar_diretorios_ftp(tipo)
    unidades = listar_cliente()

    return render_template(
        'baixar.html',
        diretorios=diretorios,
        unidades=unidades,
        link=link_cliente,
        form_data=request.form 
    )

# =========================
# ROTAS CLIENTE (UPLOAD/DOWNLOAD)
# =========================

@app.route('/upload/<token>', methods=['GET', 'POST'])
def upload_cliente(token):
    dados = buscar_token(token)
    
    # Validação do Token
    if not dados or dados[0] != "upload":
        return render_template(
            'upload.html',
            token=token,
            erro_fatal="Este link de envio não existe ou expirou."
        )

    caminho_ftp = dados[1]
    
    if request.method == 'GET':
        return render_template('upload.html', token=token, caminho_destino=caminho_ftp)

    arquivo = request.files.get('arquivo')
    
    if not arquivo:
        return render_template('upload.html', token=token, erro_fatal="Nenhum arquivo foi selecionado.")

    nome_arquivo = arquivo.filename
    ftp = FTP('ftp.dominiosistemas.com.br')

    try:
        ftp.login(user='suportesc', passwd='pmn7755')
        
        # MODO BINÁRIO E PASSIVO OBRIGATÓRIO
        ftp.set_pasv(True)
        ftp.voidcmd('TYPE I') 

        try:
            ftp.cwd(caminho_ftp)
        except error_perm:
            return render_template('upload.html', token=token, erro_fatal="A pasta de destino não foi encontrada no servidor.")

        # Tenta enviar o arquivo
        try:
            # Tenta deletar o arquivo antes para garantir que sobrescreva
            try:
                ftp.delete(nome_arquivo)
            except:
                pass 

            # === AQUI ESTÁ A CORREÇÃO PRINCIPAL ===
            # Força o ponteiro do arquivo para o início (byte 0)
            # para garantir que ele não envie um arquivo vazio se já tiver sido lido antes
            arquivo.stream.seek(0)
            
            # Usa .stream para garantir que o FTP leia o fluxo de dados corretamente
            ftp.storbinary(f"STOR {nome_arquivo}", arquivo.stream)

        except error_perm as e:
            # Tratamento de erro detalhado
            erro = str(e)
            if "Permission denied" in erro:
                msg = "Sem permissão para enviar arquivos para este local."
            elif "No such file or directory" in erro:
                msg = "A pasta de destino não existe."
            else:
                msg = f"Erro ao enviar o arquivo: {erro}"

            return render_template('upload.html', token=token, erro_fatal=msg)

        # Sucesso
        return render_template('upload.html', token=token, sucesso=True, nome_arquivo=nome_arquivo)

    except Exception as e:
        return render_template('upload.html', token=token, erro_fatal=f"Erro de conexão: {str(e)}")
        
    finally:
        try: ftp.quit()
        except: pass

@app.route('/download/<token>', methods=['GET'])
def download_cliente(token):
    dados = buscar_token(token)
    if not dados or dados[0] != "download":
        return render_template('download.html', erro_fatal="Link inválido ou expirado.", token=token, nome_arquivo="Desconhecido")
    
    caminho_ftp = dados[1].rstrip('/') 
    nome_arquivo = dados[2]
    ftp = FTP('ftp.dominiosistemas.com.br')

    try:
        ftp.login(user='suportesc', passwd='pmn7755')
        ftp.set_pasv(True) 
        ftp.voidcmd('TYPE I') 

        try: ftp.cwd(caminho_ftp)
        except error_perm: return render_template('download.html', token=token, nome_arquivo=nome_arquivo, erro_fatal="A pasta deste arquivo não existe mais no servidor.")

        try: ftp.size(nome_arquivo)
        except error_perm: return render_template('download.html', token=token, nome_arquivo=nome_arquivo, erro_fatal="O arquivo foi excluído ou movido do servidor.")

        caminho_completo = f"{caminho_ftp}/{nome_arquivo}"
        conn = ftp.transfercmd(f"RETR {caminho_completo}") 

        def gerar():
            try:
                while True:
                    bloco = conn.recv(65536) 
                    if not bloco: break 
                    yield bloco 
            finally:
                try: conn.close()
                except: pass
                try: ftp.quit()
                except: pass

        response = Response(stream_with_context(gerar()), mimetype='application/octet-stream')
        response.headers['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'
        return response

    except Exception as e:
        return render_template('download.html', token=token, nome_arquivo=nome_arquivo, erro_fatal=f"Erro de conexão com o servidor: {str(e)}")

@app.route('/download_link/<token>', methods=['GET'])
def pagina_download_cliente(token):
    dados = buscar_token(token)
    if not dados or dados[0] != "download":
        return render_template("download.html", nome_arquivo="Link Inválido", erro_fatal="Este link não existe ou foi digitado incorretamente.", token=token)

    caminho_ftp = dados[1].rstrip('/')
    nome_arquivo = dados[2]
    ftp = FTP('ftp.dominiosistemas.com.br')
    tamanho = None

    try:
        ftp.login(user='suportesc', passwd='pmn7755')
        ftp.set_pasv(True)
        ftp.voidcmd('TYPE I')
        try:
            ftp.cwd(caminho_ftp)
            tamanho = ftp.size(nome_arquivo)
        except: tamanho = None
    finally:
        try: ftp.quit()
        except: pass

    tamanho_mb = round(tamanho / (1024 * 1024), 1) if tamanho else None
    msg_erro = None
    if tamanho is None: msg_erro = "O arquivo não foi encontrado no servidor."

    return render_template("download.html", nome_arquivo=nome_arquivo, tamanho_mb=tamanho_mb, token=token, erro_fatal=msg_erro)

if __name__ == "__main__":
    app.run(debug=True)