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
            tipo TEXT,               -- upload ou download
            caminho TEXT,
            arquivo TEXT,            -- nome do arquivo (só para download)
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

    ftp.cwd('/')
    itens = []
    ftp.dir(itens.append)
    ftp.quit()

    unidades = []
    for linha in itens:
        if linha.startswith('d'):
            unidades.append(linha.split()[-1])

    return unidades


def listar_diretorios_ftp():
    ftp = FTP('ftp.dominiosistemas.com.br')
    ftp.login(user='suportesc', passwd='pmn7755')

    ftp.cwd('/clientes')
    itens = []
    ftp.dir(itens.append)
    ftp.quit()

    diretorios = []
    for linha in itens:
        if linha.startswith('d'):
            diretorios.append(linha.split()[-1])

    return diretorios


# =========================
# ROTAS
# =========================

@app.route("/")
def index():
    return render_template('index.html')


@app.route("/envio")
def envio():
    diretorios = listar_diretorios_ftp()
    unidades = listar_cliente()
    
    return render_template(
        'enviar.html',
        diretorios=diretorios,
        unidades=unidades
    )

@app.route("/baixar")
def baixar():
    diretorios = listar_diretorios_ftp()
    unidades = listar_cliente()
    
    return render_template(
        'baixar.html',
        diretorios=diretorios,
        unidades=unidades
    )

# =========================
# GERAÇÃO DE LINK
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

    token = str(uuid.uuid4())

    salvar_token(
        token=token,
        tipo="upload",
        caminho=caminho
    )

    link_cliente = url_for('upload_cliente', token=token, _external=True)

    diretorios = listar_diretorios_ftp()
    unidades = listar_cliente()

    return render_template(
        'enviar.html',
        diretorios=diretorios,
        unidades=unidades,
        link=link_cliente
    )

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

    diretorios = listar_diretorios_ftp()
    unidades = listar_cliente()

    return render_template(
        'baixar.html',
        diretorios=diretorios,
        unidades=unidades,
        link=link_cliente
    )

# =========================
# UPLOAD DO CLIENTE
# =========================

@app.route('/upload/<token>', methods=['GET', 'POST'])
def upload_cliente(token):
    dados = buscar_token(token)
    
    if not dados or dados[0] != "upload":
            return jsonify({
                "success": False,
                "message": "Link inválido."
            }), 404

    if request.method == 'GET':
        return render_template('upload.html')

    arquivo = request.files.get('arquivo')

    if not arquivo:
        return jsonify({
            "success": False,
            "message": "Nenhum arquivo enviado."
        }), 400

    caminho_ftp = dados[1]
    nome_arquivo = arquivo.filename

    ftp = FTP('ftp.dominiosistemas.com.br')

    try:
        ftp.login(user='suportesc', passwd='pmn7755')

        # tenta acessar a pasta
        try:
            ftp.cwd(caminho_ftp)
        except error_perm:
            return jsonify({
                "success": False,
                "message": "A pasta de destino não existe. Entre em contato com o suporte."
            }), 400

        # tenta apagar arquivo existente (sobrescrever)
        try:
            ftp.delete(nome_arquivo)
        except error_perm:
            pass

        ftp.storbinary(f"STOR {nome_arquivo}", arquivo)

        return jsonify({
            "success": True,
            "message": "Upload realizado com sucesso."
        }), 200

    except error_perm as e:
        erro = str(e)

        if "Permission denied" in erro:
            msg = "Sem permissão para enviar arquivos para este local."
        elif "Overwrite permission denied" in erro:
            msg = "Não é permitido sobrescrever arquivos nesta pasta."
        elif "No such file or directory" in erro:
            msg = "A pasta de destino não existe. Entre em contato com o suporte."
        else:
            msg = "Erro ao enviar o arquivo para o servidor."

        return jsonify({
            "success": False,
            "message": msg
        }), 400

    except Exception:
        return jsonify({
            "success": False,
            "message": "Erro inesperado no servidor."
        }), 500

    finally:
        try:
            ftp.quit()
        except:
            pass

# =========================
# DOWNLOAD DO CLIENTE
# =========================

@app.route('/download/<token>', methods=['GET'])
def download_cliente(token):
    dados = buscar_token(token)
    if not dados or dados[0] != "download":
        return "Link inválido.", 404
    
    caminho_ftp = dados[1].rstrip('/')
    nome_arquivo = dados[2]

    ftp = FTP('ftp.dominiosistemas.com.br')

    try:
        ftp.login(user='suportesc', passwd='pmn7755')
        ftp.set_pasv(True)
        ftp.voidcmd('TYPE I')

        try:
            ftp.cwd(caminho_ftp)
        except error_perm:
            return f"Pasta não encontrada: {caminho_ftp}", 400

        try:
            tamanho = ftp.size(nome_arquivo)
        except:
            tamanho = None

        conn = ftp.transfercmd(f"RETR {nome_arquivo}")

        def gerar():
            try:
                while True:
                    bloco = conn.recv(65536)  # 64 KB
                    if not bloco:
                        break
                    yield bloco
            finally:
                try:
                    conn.close()
                except:
                    pass
                try:
                    ftp.quit()
                except:
                    pass

        response = Response(
            stream_with_context(gerar()),
            mimetype='application/octet-stream'
        )

        response.headers['Content-Disposition'] = (
            f'attachment; filename="{nome_arquivo}"'
        )

        if tamanho is not None:
            response.headers['Content-Length'] = str(tamanho)

        return response

    except error_perm as e:
        return f"Erro FTP: {str(e)}", 404

    except Exception as e:
        return f"Erro inesperado: {str(e)}", 500
    
@app.route('/download_link/<token>', methods=['GET'])
def pagina_download_cliente(token):
    dados = buscar_token(token)
    if not dados or dados[0] != "download":
        return "Link inválido.", 404

    caminho_ftp = dados[1].rstrip('/')
    nome_arquivo = dados[2]

    ftp = FTP('ftp.dominiosistemas.com.br')
    tamanho = None

    try:
        ftp.login(user='suportesc', passwd='pmn7755')
        ftp.set_pasv(True)
        ftp.voidcmd('TYPE I')
        ftp.cwd(caminho_ftp)

        try:
            tamanho = ftp.size(nome_arquivo)
        except:
            tamanho = None
    finally:
        try:
            ftp.quit()
        except:
            pass

    tamanho_mb = round(tamanho / (1024 * 1024), 1) if tamanho else None
    return render_template(
        "download.html",
        nome_arquivo=nome_arquivo,
        tamanho_mb=tamanho_mb,
        token=token
    )
    
# =========================
# MAIN
# =========================

if __name__ == "__main__":
    app.run(debug=True)
