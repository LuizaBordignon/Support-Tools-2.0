document.addEventListener('DOMContentLoaded', function() {
    
    // --- 1. LÓGICA DO BOTÃO VOLTAR ---
    const btnVoltar = document.getElementById('btn-voltar');
    if (btnVoltar) {
        btnVoltar.addEventListener('click', function() {
            window.history.back();
        });
    }

    // --- 2. LÓGICA DE ADICIONAR SUBPASTAS (O Design Bonito) ---
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
            
            // (Opcional) Se você quiser que seja obrigatório preencher ao adicionar:
            // novoInput.required = true; 

            // Cria o Botão de Remover (X vermelho)
            const btnRemover = document.createElement('button');
            btnRemover.type = 'button';
            btnRemover.className = 'btn-remove'; // Classe do CSS novo
            btnRemover.innerHTML = '&times;'; // Símbolo de "X" (fica mais bonito que o "-")
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
        // Ou mantém visível dependendo da sua regra de negócio.
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
// Mantive fora do DOMContentLoaded para poder ser chamada pelo onclick do HTML se necessário
function copiarLink() {
    var linkElement = document.getElementById('linkCliente');
    var mensagem = document.getElementById('mensagemSucesso');
    
    if (!linkElement) return; // Segurança caso o elemento não exista

    linkElement.select();
    linkElement.setSelectionRange(0, 99999); // Para mobile

    // Tenta usar a API moderna de Clipboard
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