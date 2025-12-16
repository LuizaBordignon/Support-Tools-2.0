document.getElementById('tem_subpasta').addEventListener('change', function () {
    document.getElementById('subpasta').disabled = !this.checked;
});

function montarCaminho() {
    const tipo = document.getElementById('tipo').value;
    const unidade = document.getElementById('unidade').value;
    const codigo = document.getElementById('codigo').value;
    const temSubpasta = document.getElementById('tem_subpasta').checked;
    const subpasta = document.getElementById('subpasta').value;

    if (!tipo || !unidade || !codigo) {
        alert('Preencha todos os campos obrigatórios');
        return;
    }

    let caminho = `/${tipo}/${unidade}/${codigo}`;

    if (temSubpasta && subpasta) {
        caminho += `/${subpasta}`;
    }

    document.getElementById('resultado').innerText = caminho;
}
