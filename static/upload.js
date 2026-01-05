document.getElementById('formUpload').addEventListener('submit', function (e) {
    e.preventDefault();

    const arquivoInput = document.getElementById('arquivo');
    // Separei em duas variáveis para não misturar o "0%" com a "Mensagem final"
    const spanPorcentagem = document.getElementById('porcentagem'); 
    const divMensagem = document.getElementById('mensagem'); 

    if (!arquivoInput.files.length) {
        divMensagem.innerText = 'Selecione um arquivo.';
        divMensagem.className = 'log-box status-error'; // Fica vermelho
        return;
    }

    // Reseta a mensagem antes de começar
    divMensagem.innerText = '';
    divMensagem.className = 'log-box'; 

    const formData = new FormData();
    formData.append('arquivo', arquivoInput.files[0]);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', window.location.href);

    xhr.upload.onprogress = function (e) {
        if (e.lengthComputable) {
            const percent = Math.round((e.loaded / e.total) * 100);
            document.getElementById('barra').value = percent;
            spanPorcentagem.innerText = percent + '%'; // Atualiza só o número
        }
    };

    xhr.onload = function () {
        let resposta;

        try {
            resposta = JSON.parse(xhr.responseText);
        } catch {
            divMensagem.innerText = 'Erro inesperado no servidor.';
            divMensagem.className = 'log-box status-error'; // Fica vermelho
            return;
        }

        if (xhr.status === 200 && resposta.success) {
            // SUCESSO: Pinta de verde
            divMensagem.innerText = resposta.message;
            divMensagem.className = 'log-box status-success'; 
        } else {
            // ERRO (do backend): Pinta de vermelho
            divMensagem.innerText = resposta.message;
            divMensagem.className = 'log-box status-error'; 
        }
    };

    xhr.onerror = function () {
        divMensagem.innerText = 'Erro de conexão.';
        divMensagem.className = 'log-box status-error'; // Fica vermelho
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