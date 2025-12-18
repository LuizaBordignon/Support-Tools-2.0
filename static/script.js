document.addEventListener('DOMContentLoaded', function () {

    const checkbox = document.getElementById('tem_subpasta');
    const subpasta = document.getElementById('subpasta');

    if (checkbox && subpasta) {
        checkbox.addEventListener('change', function () {
            subpasta.disabled = !this.checked;
        });
    }

});

document.getElementById('formUpload').addEventListener('submit', function (e) {
    e.preventDefault();

    const arquivo = document.getElementById('arquivo').files[0];
    const formData = new FormData();
    formData.append('arquivo', arquivo);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', window.location.href);

    xhr.upload.onprogress = function (e) {
        if (e.lengthComputable) {
            const percent = Math.round((e.loaded / e.total) * 100);
            document.getElementById('barra').value = percent;
            document.getElementById('porcentagem').innerText = percent + '%';
        }
    };

    xhr.onload = function () {
        const resposta = JSON.parse(xhr.responseText);

        if (xhr.status === 200 && resposta.success) {
            document.getElementById('porcentagem').innerText =
                resposta.message;
        } else {
            document.getElementById('porcentagem').innerText =
                'Erro: ' + resposta.message;
        }
    };

    xhr.send(formData);
});

document.getElementById('form-upload').addEventListener('submit', async function (e) {
    e.preventDefault();

    const formData = new FormData(this);

    try {
        const response = await fetch(window.location.href, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        const msg = document.getElementById('mensagem');
        msg.textContent = data.message;
        msg.style.color = data.success ? 'green' : 'red';

    } catch (err) {
        document.getElementById('mensagem').textContent =
            'Erro inesperado ao enviar o arquivo.';
    }
});

