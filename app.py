from flask import Flask, render_template, request, url_for, jsonify, send_file
from ftplib import FTP, error_perm
import uuid, tempfile, os

app = Flask(__name__)

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

links = {}

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
    links[token] = caminho

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
    subpastas = request.form.getlist('subpasta[]')

    if not tipo or not unidade or not codigo:
        return "Campos obrigatórios não preenchidos", 400

    caminho = f"/{tipo}/{unidade}/{codigo}"
    for subpasta in subpastas:
        if subpasta.strip():
            caminho += f"/{subpasta.strip()}"

    token = str(uuid.uuid4())
    links[token] = caminho

    link_cliente = url_for(
        'download_cliente',
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
    if token not in links:
        return jsonify({
            "success": False,
            "message": "Link inválido ou expirado."
        }), 404

    if request.method == 'GET':
        return render_template('upload.html')

    arquivo = request.files.get('arquivo')

    if not arquivo:
        return jsonify({
            "success": False,
            "message": "Nenhum arquivo enviado."
        }), 400

    caminho_ftp = links[token]
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
                "message": "A pasta de destino não existe. Verifique o caminho informado."
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
    if token not in links:
        return "Link inválido ou expirado.", 404

    caminho_ftp = links[token]

    ftp = FTP('ftp.dominiosistemas.com.br')

    try:
        ftp.login(user='suportesc', passwd='pmn7755')

        # entra na pasta onde está o backup
        try:
            ftp.cwd(caminho_ftp)
        except error_perm:
            return "A pasta do backup não existe.", 400

        # lista arquivos da pasta
        arquivos = ftp.nlst()

        if not arquivos:
            return "Nenhum backup encontrado nesta pasta.", 404

        # regra simples: pegar o primeiro arquivo
        nome_arquivo = arquivos[0]

        # cria arquivo temporário
        temp_dir = tempfile.gettempdir()
        caminho_local = os.path.join(temp_dir, nome_arquivo)

        with open(caminho_local, 'wb') as f:
            ftp.retrbinary(f"RETR {nome_arquivo}", f.write)

        return send_file(
            caminho_local,
            as_attachment=True,
            download_name=nome_arquivo
        )

    except error_perm:
        return "Erro de permissão ao acessar o backup.", 400

    except Exception:
        return "Erro inesperado ao baixar o backup.", 500

    finally:
        try:
            ftp.quit()
        except:
            pass


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    app.run(debug=True)
