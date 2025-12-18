from flask import Flask, render_template, request, url_for, abort
from ftplib import FTP
import uuid

app = Flask(__name__)

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
            nome = linha.split()[-1]
            unidades.append(nome)

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
            nome = linha.split()[-1]
            diretorios.append(nome)

    return diretorios

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/envio")
def envio():
    diretorios = listar_diretorios_ftp()
    unidades = listar_cliente()
    return render_template('enviar.html', diretorios=diretorios, unidades=unidades)

links = {}

@app.route('/gerar_link', methods=['POST'])
def gerar_link():
    tipo = request.form.get('tipo')
    unidade = request.form.get('unidade')
    codigo = request.form.get('codigo')
    subpasta = request.form.get('subpasta')

    if not tipo or not unidade or not codigo:
        return "Campos obrigatórios não preenchidos", 400

    caminho = f"/{tipo}/{unidade}/{codigo}"
    if subpasta:
        caminho += f"/{subpasta}"

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


@app.route('/upload/<token>', methods=['GET', 'POST'])
def upload_cliente(token):
    if token not in links:
        return abort(404)

    if request.method == 'GET':
        return render_template('upload.html')

    arquivo = request.files.get('arquivo')

    if not arquivo:
        return "Nenhum arquivo enviado", 400

    caminho_ftp = links[token]

    ftp = FTP('ftp.dominiosistemas.com.br')
    ftp.login(user='suportesc', passwd='pmn7755')

    ftp.cwd(caminho_ftp)
    ftp.storbinary(f"STOR {arquivo.filename}", arquivo)

    ftp.quit()

    return "Upload realizado com sucesso"

if __name__ == "__main__":

    app.run(debug=True)