document.addEventListener("DOMContentLoaded", function() {
    const formGroups = document.querySelectorAll(".form-group");

    formGroups.forEach(group => {
        const label = group.querySelector("label");
        const input = group.querySelector("input, select, textarea");

        if (label && input) {
            const labelWidth = label.offsetWidth;
            input.style.paddingLeft = `${labelWidth + 16}px`; // 16px de espaçamento adicional
        }
    });
});



document.addEventListener('DOMContentLoaded', function() {
    function verificarCondicoes() {
        let camposCondicionais = document.querySelectorAll('[data-condicao]');
        camposCondicionais.forEach(campo => {
            let condicoes = JSON.parse(campo.dataset.condicao);
            let conditionsMet = true;

            if (typeof condicoes === 'object' && !Array.isArray(condicoes)) {
                condicoes = Object.entries(condicoes).map(([chave, valor]) => {
                    return { [chave]: valor };
                });
            }

            conditionsMet = condicoes.every(condicao => {
                let [chave, valorEsperado] = Object.entries(condicao)[0];
                let elementoControlador = document.getElementById(chave);

                if (!elementoControlador) {
                    return false;
                }

                let valorAtual = elementoControlador.value.toString().trim().toLowerCase();
                let esperado = Array.isArray(valorEsperado) ? valorEsperado.map(val => val.toString().trim().toLowerCase()) : [valorEsperado.toString().trim().toLowerCase()];

                // Verificando se o valor esperado é booleano
                if (typeof valorEsperado === "boolean") {
                    if (valorEsperado) {
                        return valorAtual !== "";
                    } else {
                        return valorAtual === "";
                    }
                }

                return esperado.includes(valorAtual);
            });

            if (conditionsMet) {
                campo.style.display = "block";
                let input = campo.querySelector('input, select, textarea');
                if (input) input.disabled = false;
            } else {
                campo.style.display = "none";
                let input = campo.querySelector('input, select, textarea');
                if (input) input.disabled = true;
            }
        });
    }

    document.querySelectorAll('input, select').forEach(elemento => {
        elemento.addEventListener('change', verificarCondicoes);
    });

    verificarCondicoes();
});



function showPopup(message, fileUrl = null) {
    // Exibe a mensagem no popup
    document.getElementById('popup-message').innerText = message;

    const downloadLink = document.getElementById('download-button');

    // Se um arquivo URL foi retornado, exibe o link para download
    if (fileUrl) {
        downloadLink.style.display = 'block';  // Exibe o link de download
        downloadLink.href = fileUrl;  // Define o URL do arquivo

        // Opcional: Exibe uma mensagem ou outros detalhes no popup
    } else {
        downloadLink.style.display = 'none';  // Oculta o link se não houver URL
    }

    // Exibe o overlay e o popup
    document.querySelector('.popup-overlay').style.display = 'block';
    document.getElementById('popup').style.display = 'block';
}

function closePopup() {
    // Fecha o popup
    document.querySelector('.popup-overlay').style.display = 'none';
    document.getElementById('popup').style.display = 'none';
    document.getElementById('download-link').style.display = 'none';  // Esconde o link de download
}

$(document).ready(function () {
    $('#dynamicForm').submit(function (event) {
        event.preventDefault(); // Impede o envio padrão do formulário

        const formData = $(this).serialize();

        $.ajax({
            url: $(this).attr('action'), // Usa o valor de `action` do formulário
            type: 'POST',
            data: formData,
            success: function (response) {
                // Se a URL do arquivo foi retornada corretamente
                if (response.file_url) {
                    showPopup('O arquivo DOCX foi gerado com sucesso!', response.file_url);
                } else {
                    showPopup('Ocorreu um erro ao gerar o arquivo DOCX.');
                }
            },
            error: function (xhr, status, error) {
                showPopup('Ocorreu um erro: ' + error);
            }
        });
    });
});
