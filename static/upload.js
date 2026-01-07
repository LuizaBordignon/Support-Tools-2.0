document.getElementById('formUpload').addEventListener('submit', function (e) {
    e.preventDefault();

    const arquivoInput = document.getElementById('arquivo');
    const spanPorcentagem = document.getElementById('porcentagem'); 
    const divMensagem = document.getElementById('mensagem'); 
    const statusText = document.getElementById('status-text');
    const barra = document.getElementById('barra');
    
    // Pegamos os elementos novos
    const progressArea = document.getElementById('progress-area');
    const loadingArea = document.getElementById('loading-area');
    const btnSubmit = document.querySelector('.btn-submit');

    if (!arquivoInput.files.length) {
        divMensagem.innerText = 'Selecione um arquivo.';
        divMensagem.className = 'log-box status-error';
        return;
    }

    // Reset visual
    divMensagem.innerText = '';
    divMensagem.className = 'log-box';
    barra.value = 0;
    spanPorcentagem.innerText = '0%';
    statusText.innerText = 'Iniciando envio...';
    
    // Garante que o loading está oculto e a barra visível no início
    loadingArea.style.display = 'none';
    progressArea.style.display = 'block'; 
    btnSubmit.disabled = true; // Desabilita botão para não clicar 2x
    btnSubmit.style.opacity = '0.6';

    const formData = new FormData();
    formData.append('arquivo', arquivoInput.files[0]);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', window.location.href);

    xhr.upload.onprogress = function (e) {
        if (e.lengthComputable) {
            const percent = Math.round((e.loaded / e.total) * 100);

            barra.value = percent;
            spanPorcentagem.innerText = percent + '%';

            // --- MUDANÇA AQUI: Lógica de troca visual ---
            if (percent < 100) {
                statusText.innerText = 'Enviando arquivo...';
            } else {
                // Chegou em 100%: Esconde a barra e mostra a rodinha
                progressArea.style.display = 'none'; 
                loadingArea.style.display = 'block';
            }
        }
    };

    xhr.onload = function () {
        // Quando o servidor finalmente responde (terminou tudo)
        // Escondemos o loading também
        loadingArea.style.display = 'none';
        btnSubmit.disabled = false;
        btnSubmit.style.opacity = '1';

        let resposta;

        try {
            resposta = JSON.parse(xhr.responseText);
        } catch {
            divMensagem.innerText = 'Erro inesperado no servidor.';
            divMensagem.className = 'log-box status-error';
            return;
        }

        if (xhr.status === 200 && resposta.success) {
            divMensagem.innerText = resposta.message;
            divMensagem.className = 'log-box status-success';
            // Opcional: Limpar o input file após sucesso
            // arquivoInput.value = ''; 
        } else {
            divMensagem.innerText = resposta.message;
            divMensagem.className = 'log-box status-error';
        }
    };

    xhr.onerror = function () {
        loadingArea.style.display = 'none';
        progressArea.style.display = 'none';
        btnSubmit.disabled = false;
        btnSubmit.style.opacity = '1';
        
        divMensagem.innerText = 'Erro de conexão.';
        divMensagem.className = 'log-box status-error';
    };

    xhr.send(formData);
});

// Nome do arquivo 
const inputFile = document.getElementById('arquivo');
const fileNameDisplay = document.getElementById('file-name-display');

inputFile.addEventListener('change', function() {
    if (this.files && this.files.length > 0) {
        fileNameDisplay.textContent = this.files[0].name;
        fileNameDisplay.style.color = "#333";
        fileNameDisplay.style.fontWeight = "600";
    } else {
        fileNameDisplay.textContent = "Nenhum arquivo selecionado";
     }
});