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
                    // Exemplo de popup com link para download do arquivo
                    popup.Open_PopUp({
                        type: 'success', // Tipo do popup, pode ser 'success', 'error', 'neutral'
                        message: 'O arquivo DOCX foi gerado com sucesso!',
                        buttons: [{
                            label: 'Baixar DOCX',
                            action: function () {
                                window.location.href = response.file_url; // Redireciona para o link do arquivo
                            },
                            close: true // Fecha o popup após clicar no botão
                        }],
                        autoClose: 0 // Opcional: se não precisar de um tempo para fechar, pode deixar 0
                    });
                } else {
                    // Exemplo de popup sem link, caso haja erro
                    popup.Open_PopUp({
                        type: 'error', // Tipo do popup
                        message: 'Ocorreu um erro ao gerar o arquivo DOCX.',
                        buttons: [{
                            label: 'Fechar',
                            action: function () {
                                // Função de fechamento (não precisa de ação extra aqui)
                            },
                            close: true
                        }],
                        autoClose: 0
                    });
                }
            },
            error: function (xhr, status, error) {
                // Exibe um popup de erro
                popup.Open_PopUp({
                    type: 'error',
                    message: 'Ocorreu um erro: ' + error,
                    buttons: [{
                        label: 'Fechar',
                        action: function () {
                            // Função de fechamento (não precisa de ação extra aqui)
                        },
                        close: true
                    }],
                    autoClose: 0
                });
            }
        });
    });
});
