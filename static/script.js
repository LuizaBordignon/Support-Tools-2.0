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
        if (xhr.status === 200) {
            document.getElementById('porcentagem').innerText = 'Upload concluído';
        } else {
            document.getElementById('porcentagem').innerText = 'Erro no upload';
        }
    };

    xhr.send(formData);
});

