
// copiar link do cliente

function copiarLink() {
    var linkElement = document.getElementById('linkCliente');
    var mensagem = document.getElementById('mensagemSucesso');
    linkElement.select();

   navigator.clipboard.writeText(linkElement.value).then(() => {
        // Mostra a mensagem de sucesso
        mensagem.style.display = "block";
        
        // Esconde a mensagem após 2 segundos
        setTimeout(() => {
            mensagem.style.display = "none";
        }, 2000);

    }).catch(err => {
        // Fallback: Caso a API falhe ou o navegador seja antigo
        console.error('Erro ao copiar: ', err);
        try {
            document.execCommand('copy');
            mensagem.style.display = "block";
        } catch (e) {
            alert("Erro ao copiar o link.");
        }
    });
}

// campo adicionar mais uma subpasta
const btnAdicionar = document.getElementById('btn-adicionar')
const container = document.getElementById('lista-campos');

btnAdicionar.addEventListener('click', function() {
    const novoDiv = document.createElement('div');
    novoDiv.className = 'grupo-input';

    const novoInput = document.createElement('input');
    novoInput.type = 'text';
    novoInput.name = 'subpasta[]';
    novoInput.placeholder = 'Subpasta (opcional)';
    novoInput.required = true;

    const btnRemover = document.createElement('button');
    btnRemover.type = 'button';
    btnRemover.className = 'btn-remove';
    btnRemover.innerText = '-';
    btnRemover.title = 'Remover este campo';

    btnRemover.addEventListener('click', function() {
        container.removeChild(novoDiv);
     });

    // Monta os elementos na tela
    novoDiv.appendChild(novoInput);
    novoDiv.appendChild(btnRemover);
    container.appendChild(novoDiv);
});

document.addEventListener("DOMContentLoaded", () => {
    const bloco = document.getElementById("blocoLink");

    if (bloco) {
        if (sessionStorage.getItem("link_ja_mostrado")) {
            bloco.remove();
        } else {
            sessionStorage.setItem("link_ja_mostrado", "true");
        }
    }
});

document.querySelector("form").addEventListener("submit", () => {
    sessionStorage.removeItem("link_ja_mostrado");
});

// botão de voltar a pagina 
const btnVoltar = document.getElementById('btn-voltar')
btnVoltar.addEventListener('click', function(){
    window.history.back()
});

