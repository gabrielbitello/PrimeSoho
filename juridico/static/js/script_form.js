document.addEventListener("DOMContentLoaded", function() {
    const main = document.querySelector("main");
    const divs = main.querySelectorAll("div");

    divs.forEach(group => {
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
        // Seleciona todos os elementos com data-condicao dentro de main
        let camposCondicionais = document.querySelectorAll('main *[data-condicao]');
        
        camposCondicionais.forEach(campo => {
            let condicoesStr = campo.dataset.condicao;

            // Se o campo não tiver a condição ou estiver com erro
            if (!condicoesStr) {
                return;
            }

            let condicoes;
            try {
                condicoes = JSON.parse(condicoesStr); // Parse do JSON
            } catch (e) {
                return; // Se ocorrer erro ao analisar, ignore o campo
            }

            let conditionsMet = true;

            // Caso as condições estejam em formato de objeto, converta para uma lista simplificada
            if (typeof condicoes === 'object' && !Array.isArray(condicoes)) {
                condicoes = Object.entries(condicoes).map(([chave, valor]) => {
                    return { [chave]: valor };
                });
            }

            // Agora, vamos manipular as condições com base no novo formato
            conditionsMet = condicoes.some(condicao => {
                console.log(`Verificando condição:`, condicao); // Depuração para ver o valor real de `condicao`
            
                // Obter todas as chaves do objeto
                let chaves = Object.keys(condicao);
                
                // Verifica se a condição é uma string e contém '/'
                if (chaves.some(chave => chave.includes('/'))) {
                    console.log(`A condição "${chaves}" contém '/'`); // Depuração para confirmar o que está acontecendo
            
                    // Para cada chave que contém '/', divida a chave e extraia o que está antes da barra
                    let resultadoCondicao = chaves.some(chave => {
                        let partesChave = chave.split('/'); // Divida a chave na barra
            
                        // Agora, vamos processar cada parte da chave
                        return partesChave.some((parteChave, index) => {
                            // Pegue o valor esperado da condição para cada parte da chave
                            let valorEsperado = condicao[chave].toString().trim().toLowerCase(); 
            
                            // Verifica se o campo realmente existe no DOM
                            let elementoControlador = document.getElementById(parteChave);
                            if (!elementoControlador) {
                                console.log(`Campo ${parteChave} não encontrado.`);
                                return false; // Retorna falso se o campo não for encontrado
                            }
            
                            // Obtém o valor do campo
                            let valorAtual = elementoControlador.value.toString().trim().toLowerCase();
                            
                            console.log(`Verificando campo ${parteChave}: Valor Atual = ${valorAtual}, Valor Esperado = ${valorEsperado}`);
            
                            // Comparar o valor atual com o valor esperado
                            return valorAtual === valorEsperado;
                        });
                    });
            
                    console.log(`Resultado para a condição "${condicao}": ${resultadoCondicao}`);
                    return resultadoCondicao;
                }
            
                // Caso contrário, se for uma condição simples de campo-valor
                let [chave, valorEsperado] = Object.entries(condicao)[0];
                let elementoControlador = document.getElementById(chave);

                if (!elementoControlador) {
                    return false;
                }

                let valorAtual = elementoControlador.value.toString().trim().toLowerCase();
                let esperado = Array.isArray(valorEsperado) ? valorEsperado.map(val => val.toString().trim().toLowerCase()) : [valorEsperado.toString().trim().toLowerCase()];

                return esperado.includes(valorAtual);
            });

            // Agora verificamos a div que contém tanto o campo quanto o label
            let divContainer = campo.closest('div');
            let label = divContainer ? divContainer.querySelector('label') : null;

            if (conditionsMet) {
                // Exibe o campo e o label
                campo.style.display = "block";
                if (label) label.style.display = "block"; // Mostra o label se a condição for atendida
                
                let input = campo.querySelector('input, select, textarea, datalist, checkbox'); // Inclui mais tipos de elementos conforme necessário
                if (input) input.disabled = false;
            } else {
                // Esconde o campo e o label
                campo.style.display = "none";
                if (label) label.style.display = "none"; // Esconde o label também
                
                let input = campo.querySelector('input, select, textarea, datalist, checkbox'); // Inclui mais tipos de elementos conforme necessário
                if (input) input.disabled = true;
            }
        });
    }

    // Ouvinte de evento para campos de input, select, checkbox, etc.
    document.querySelectorAll('input, select, textarea, checkbox, datalist').forEach(elemento => {
        elemento.addEventListener('change', verificarCondicoes);
    });

    // Executa a verificação inicial
    verificarCondicoes();
});







const api = new HttpClient('/j/formulario/');

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("dynamicForm");

    form.addEventListener("submit", async function (event) {
        event.preventDefault(); // Impede o envio padrão do formulário

        const formData = new FormData(form);
        const actionUrl = form.getAttribute("action"); // Obtém a URL do atributo 'action'
        let lastSegment = actionUrl.split('/').filter(Boolean).pop(); // Obtém o último segmento após o último '/'

        // Verifica se o último segmento não termina com '/' e adiciona
        if (lastSegment.charAt(lastSegment.length - 1) !== '/') {
            lastSegment += '/';
        }

        console.log(lastSegment);


        // Converte FormData para um objeto simples que pode ser passado para o HttpClient
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });

        try {
            const response = await api.post(lastSegment, data); // Envia como dados de formulário

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
