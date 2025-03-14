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







const api = new HttpClient('/');

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("dynamicForm");

    form.addEventListener("submit", async function (event) {
        event.preventDefault(); // Impede o envio padrão do formulário

        const formData = new FormData(form);
        const actionUrl = form.getAttribute("action"); // Obtém a URL do atributo 'action'

        try {
            const response = await api.post(actionUrl, formData);

            if (response.file_url) {
                popup.Open_PopUp({
                    type: "success",
                    message: "O arquivo DOCX foi gerado com sucesso!",
                    buttons: [{
                        label: "Baixar DOCX",
                        action: () => window.location.href = response.file_url,
                        close: true
                    }],
                    autoClose: 0
                });
            } else {
                popup.Open_PopUp({
                    type: "error",
                    message: "Ocorreu um erro ao gerar o arquivo DOCX.",
                    buttons: [{ label: "Fechar", action: () => {}, close: true }],
                    autoClose: 0
                });
            }
        } catch (error) {
            popup.Open_PopUp({
                type: "error",
                message: `Ocorreu um erro: ${error.message}`,
                buttons: [{ label: "Fechar", action: () => {}, close: true }],
                autoClose: 0
            });
        }
    });
});
