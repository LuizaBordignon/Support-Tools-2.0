document.getElementById('formUpload').addEventListener('submit', function (e) {
    e.preventDefault();

    const arquivoInput = document.getElementById('arquivo');
    const mensagem = document.getElementById('porcentagem');

    if (!arquivoInput.files.length) {
        mensagem.innerText = 'Selecione um arquivo.';
        return;
    }

    const formData = new FormData();
    formData.append('arquivo', arquivoInput.files[0]);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', window.location.href);

    xhr.upload.onprogress = function (e) {
        if (e.lengthComputable) {
            const percent = Math.round((e.loaded / e.total) * 100);
            document.getElementById('barra').value = percent;
            mensagem.innerText = percent + '%';
        }
    };

    xhr.onload = function () {
        let resposta;

        try {
            resposta = JSON.parse(xhr.responseText);
        } catch {
            mensagem.innerText = 'Erro inesperado no servidor.';
            return;
        }

        if (xhr.status === 200 && resposta.success) {
            mensagem.innerText = resposta.message;
        } else {
            mensagem.innerText = resposta.message;
        }
    };

    xhr.onerror = function () {
        mensagem.innerText = 'Erro de conexão.';
    };

    xhr.send(formData);
});

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