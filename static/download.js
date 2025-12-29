document.addEventListener("DOMContentLoaded", function () {
    const botao = document.getElementById('btnBaixar');
    const barra = document.getElementById('barra');
    const mensagem = document.getElementById('porcentagem');

    console.log("JS ativo");

    botao.addEventListener('click', function () {
        console.log("Clique detectado");

        barra.value = 0;
        mensagem.innerText = '0%';

        const xhr = new XMLHttpRequest();
        xhr.open(
            'GET',
            window.location.pathname.replace('/download_link/', '/download/')
        );
        xhr.responseType = 'blob';

        xhr.onprogress = function (e) {
            console.log("Progresso", e.loaded, e.total);
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                barra.value = percent;
                mensagem.innerText = percent + '%';
            }
        };

        xhr.onload = function () {
            if (xhr.status === 200) {
                const blob = xhr.response;
                const url = URL.createObjectURL(blob);

                const a = document.createElement('a');
                a.href = url;
                a.download = '';
                document.body.appendChild(a);
                a.click();
                a.remove();

                URL.revokeObjectURL(url);
                mensagem.innerText = 'Download concluído.';
            } else {
                mensagem.innerText = 'Erro ao baixar.';
            }
        };

        xhr.send();
    });
});
