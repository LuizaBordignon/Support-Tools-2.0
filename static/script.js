document.addEventListener('DOMContentLoaded', function() {
    
    // --- 1. LÓGICA DO BOTÃO VOLTAR ---
    const btnVoltar = document.getElementById('btn-voltar');
    if (btnVoltar) {
        btnVoltar.addEventListener('click', function() {
            window.history.back();
        });
    }

    // --- 2. LÓGICA DE ADICIONAR SUBPASTAS ---
    const btnAdicionar = document.getElementById('btn-adicionar');
    const container = document.getElementById('lista-campos');

    if (btnAdicionar && container) {
        btnAdicionar.addEventListener('click', function() {
            
            // Cria a div container da linha (para alinhar input e botão)
            const novoDiv = document.createElement('div');
            novoDiv.className = 'dynamic-row'; // Classe do CSS novo

            // Cria o Input com o visual novo
            const novoInput = document.createElement('input');
            novoInput.type = 'text';
            novoInput.name = 'subpasta[]';
            novoInput.className = 'form-control'; // Classe do CSS novo
            novoInput.placeholder = 'Nome da subpasta';

            // Cria o Botão de Remover (X vermelho)
            const btnRemover = document.createElement('button');
            btnRemover.type = 'button';
            btnRemover.className = 'btn-remove'; // Classe do CSS novo
            btnRemover.innerHTML = '&times;';
            btnRemover.title = 'Remover este campo';

            // Lógica para remover a linha ao clicar no botão
            btnRemover.addEventListener('click', function() {
                container.removeChild(novoDiv);
            });

            // Monta os elementos na tela
            novoDiv.appendChild(novoInput);
            novoDiv.appendChild(btnRemover);
            container.appendChild(novoDiv);

            // Já coloca o cursor no campo novo para facilitar
            novoInput.focus();
        });
    }

    // --- 3. CONTROLE DE EXIBIÇÃO DO LINK (Sua lógica de SessionStorage) ---
    const bloco = document.getElementById("blocoLink");
    
    if (bloco) {
        // Se já mostramos o link antes e demos refresh, esconde (para não duplicar ou confundir)
        // A lógica abaixo remove o bloco se a flag 'link_ja_mostrado' existir.
        if (sessionStorage.getItem("link_ja_mostrado")) {
             bloco.remove();
        } else {
            sessionStorage.setItem("link_ja_mostrado", "true");
        }
    }

    // Limpa a sessão quando o formulário for enviado novamente
    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", () => {
            sessionStorage.removeItem("link_ja_mostrado");
        });
    }
});

// --- 4. FUNÇÃO DE COPIAR LINK ---
function copiarLink() {
    var linkElement = document.getElementById('linkCliente');
    var mensagem = document.getElementById('mensagemSucesso');
    
    if (!linkElement) return; // Segurança caso o elemento não exista

    linkElement.select();
    linkElement.setSelectionRange(0, 99999);

    // API moderna de Clipboard
    if (navigator.clipboard) {
        navigator.clipboard.writeText(linkElement.value).then(() => {
            mostrarMensagemSucesso(mensagem);
        }).catch(err => {
            console.error('Erro API Clipboard: ', err);
            fallbackCopy(linkElement, mensagem);
        });
    } else {
        // Fallback para navegadores antigos
        fallbackCopy(linkElement, mensagem);
    }
}

function fallbackCopy(inputElement, mensagemElement) {
    try {
        document.execCommand('copy');
        mostrarMensagemSucesso(mensagemElement);
    } catch (e) {
        alert("Não foi possível copiar automaticamente.");
    }
}

function mostrarMensagemSucesso(elementoMensagem) {
    if (elementoMensagem) {
        elementoMensagem.style.display = "block";
        setTimeout(() => {
            elementoMensagem.style.display = "none";
        }, 2000);
    }
}

document.querySelector('select[name="tipo"]').addEventListener('change', function () {
    const tipo = this.value;
    const selectUnidade = document.querySelector('select[name="unidade"]');

    selectUnidade.innerHTML = '<option disabled selected>Carregando...</option>';

    fetch(`/listar_diretorios/${tipo}`)
        .then(res => res.json())
        .then(dados => {
            selectUnidade.innerHTML = '<option disabled selected>Selecione a unidade</option>';

            dados.forEach(dir => {
                const opt = document.createElement('option');
                opt.value = dir;
                opt.textContent = dir;
                selectUnidade.appendChild(opt);
            });
        });
});


function criarPastaViaJs(btnElement) {
    const caminho = document.getElementById('caminho-oculto').value;
    const divResultado = document.getElementById('resultado-criacao');
    
    // Efeito visual de carregamento
    const textoOriginal = btnElement.innerHTML;
    btnElement.disabled = true;
    btnElement.innerHTML = "Criando...";
    divResultado.innerHTML = ""; // Limpa mensagens anteriores

    // Prepara os dados como se fosse um formulário (para o Python entender request.form)
    const dados = new URLSearchParams();
    dados.append('caminho', caminho);

    fetch('/criar_pasta', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: dados
    })
    .then(response => response.json())
    .then(data => {
        // Restaura o botão
        btnElement.disabled = false;
        btnElement.innerHTML = textoOriginal;

        if (data.sucesso) {
            // Sucesso: Mostra mensagem verde e esconde o botão de criar
            divResultado.innerHTML = `
                <div class="status-success" style="animation: fadeIn 0.5s ease;">
                    Pasta criada com sucesso! <br>
                    <strong>Tente clicar em "Gerar Link" novamente.</strong>
                </div>
            `;
            // Opcional: Esconder o botão de criar pasta após o sucesso para não clicar de novo
            btnElement.style.display = 'none';
        } else {
            // Erro: Mostra mensagem vermelha vinda do Python
            divResultado.innerHTML = `
                <div class="status-error" style="animation: fadeIn 0.5s ease;">
                    Erro: ${data.erro}
                </div>
            `;
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        btnElement.disabled = false;
        btnElement.innerHTML = textoOriginal;
        divResultado.innerHTML = `
            <div class="status-error">
                Erro de conexão ao tentar criar a pasta.
            </div>
        `;
    });
}

