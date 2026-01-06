document.getElementById('formUpload').addEventListener('submit', function (e) {
    e.preventDefault();

    const arquivoInput = document.getElementById('arquivo');
    const spanPorcentagem = document.getElementById('porcentagem'); 
    const divMensagem = document.getElementById('mensagem'); 
    const statusText = document.getElementById('status-text');
    const barra = document.getElementById('barra');

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

    const formData = new FormData();
    formData.append('arquivo', arquivoInput.files[0]);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', window.location.href);

    xhr.upload.onprogress = function (e) {
        if (e.lengthComputable) {
            const percent = Math.round((e.loaded / e.total) * 100);

            barra.value = percent;
            spanPorcentagem.innerText = percent + '%';

            if (percent < 100) {
                statusText.innerText = 'Enviando arquivo...';
            } else {
                statusText.innerText = 'Arquivo enviado. Finalizando processamento no servidor...';
            }
        }
    };

    xhr.onload = function () {
        let resposta;

        try {
            resposta = JSON.parse(xhr.responseText);
        } catch {
            statusText.innerText = 'Erro inesperado.';
            divMensagem.innerText = 'Erro inesperado no servidor.';
            divMensagem.className = 'log-box status-error';
            return;
        }

        if (xhr.status === 200 && resposta.success) {
            statusText.innerText = 'Upload realizado com sucesso!';
            divMensagem.innerText = resposta.message;
            divMensagem.className = 'log-box status-success';
        } else {
            statusText.innerText = 'Erro no envio.';
            divMensagem.innerText = resposta.message;
            divMensagem.className = 'log-box status-error';
        }
    };

    xhr.onerror = function () {
        statusText.innerText = 'Erro de conexão.';
        divMensagem.innerText = 'Erro de conexão.';
        divMensagem.className = 'log-box status-error';
    };

    xhr.send(formData);
});


// Mantive seu código de visualização do nome do arquivo intacto
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