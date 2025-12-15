from flask import Flask, render_template
from ftplib import FTP

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

if __name__ == "__main__":
    app.run(debug=True)