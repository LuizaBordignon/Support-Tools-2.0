document.addEventListener("DOMContentLoaded", function () {
    const botao = document.getElementById("btnBaixar");

    botao.addEventListener("click", function () {
        console.log("REDIRECIONANDO PARA:", DOWNLOAD_URL);
        window.location.href = DOWNLOAD_URL;
    });
});
