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
    // Função para aplicar a lógica de condições a um elemento
    function aplicarCondicoes(elemento) {
        let camposCondicionais = elemento.querySelectorAll('*[data-condicao]');

        camposCondicionais.forEach((campo) => {
            let condicoesStr = campo.dataset.condicao;

            if (!condicoesStr) return;

            let condicoes;
            try {
                condicoes = JSON.parse(condicoesStr);
            } catch (e) {
                console.error("Erro ao analisar condição:", e);
                return;
            }

            let conditionsMet = Array.isArray(condicoes) 
                ? condicoes.some(condicao => verificaCondicaoUnica(condicao))
                : Object.entries(condicoes).every(([chave, valor]) => verificaCondicaoUnica({[chave]: valor}));

            let inputs = campo.matches('input, select, textarea') ? [campo] : campo.querySelectorAll('input, select, textarea');
            let divContainer = campo.closest('div');

            if (conditionsMet) {
                campo.style.display = "block";
                inputs.forEach(input => input.disabled = false);
                if (divContainer) {
                    divContainer.querySelectorAll('label').forEach(label => label.style.display = "block");
                }
            } else {
                campo.style.display = "none";
                inputs.forEach(input => input.disabled = true);
                if (divContainer) {
                    divContainer.querySelectorAll('label').forEach(label => label.style.display = "none");
                }
            }
        });
    }

    function verificaCondicaoUnica(condicao) {
        let [chave, valorEsperado] = Object.entries(condicao)[0];

        if (chave.includes('/')) {
            return chave.split('/').some(parteChave => verificaCampo(parteChave, valorEsperado));
        }

        return verificaCampo(chave, valorEsperado);
    }

    function verificaCampo(chave, valorEsperado) {
        let elementoControlador = document.getElementById(chave);
        if (!elementoControlador) {
            console.warn(`Campo controlador não encontrado: ${chave}`);
            return false;
        }

        if (elementoControlador.type === 'checkbox') {
            return elementoControlador.checked === (valorEsperado === true || valorEsperado === 'true');
        } else {
            let valorAtual = elementoControlador.value.toString().trim().toLowerCase();
            let esperado = Array.isArray(valorEsperado) 
                ? valorEsperado.map(val => val.toString().trim().toLowerCase())
                : [valorEsperado.toString().trim().toLowerCase()];
            return esperado.includes(valorAtual);
        }
    }

    function adicionarOuvintes(elemento) {
        elemento.querySelectorAll('input, select, textarea').forEach(el => {
            el.addEventListener('change', () => aplicarCondicoes(document.querySelector('main')));
        });
    }

    // Configuração do MutationObserver
    const config = { childList: true, subtree: true };
    const callback = function(mutationsList, observer) {
        for(let mutation of mutationsList) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        aplicarCondicoes(node);
                        adicionarOuvintes(node);
                    }
                });
            }
        }
    };

    // Criar e iniciar o MutationObserver
    const observer = new MutationObserver(callback);
    observer.observe(document.querySelector('main'), config);

    // Aplicação inicial
    aplicarCondicoes(document.querySelector('main'));
    adicionarOuvintes(document.querySelector('main'));
});












document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.multiplicador').forEach(function(button) {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            const buttonId = this.id;
            const inputQuantidade = document.getElementById(buttonId);
            if (!inputQuantidade) {
                console.error(`Input com ID "${buttonId}" não encontrado`);
                return;
            }

            let quantidadeDesejada = Math.max(1, parseInt(inputQuantidade.value) || 1);
            inputQuantidade.value = quantidadeDesejada;

            const grupo = this.getAttribute('data-grupo');
            if (!grupo) {
                return;
            }

            const formset = document.querySelector(`div[data-grupo="${grupo}"]`);
            if (!formset) {
                console.error(`Formset para grupo "${grupo}" não encontrado`);
                return;
            }

            const forms = formset.querySelectorAll('.formset-form');
            const quantidadeAtual = forms.length;

            const totalForms = formset.querySelector('[name$="-TOTAL_FORMS"]');
            if (!totalForms) {
                console.error(`Campo de total de formulários não encontrado para o grupo "${grupo}"`);
                return;
            }

            // Função para atualizar IDs, nomes e condições
            function atualizarFormulario(form, novoIndice) {
                form.querySelectorAll('*').forEach(element => {
                    ['name', 'id', 'for'].forEach(attr => {
                        if (element.hasAttribute(attr)) {
                            element.setAttribute(attr, element.getAttribute(attr).replace(/\d+/, novoIndice));
                        }
                    });

                    if (element.dataset && element.dataset.condicao) {
                        try {
                            let condicoes = JSON.parse(element.dataset.condicao);
                            condicoes = atualizarChavesCondicoes(condicoes, novoIndice);
                            element.dataset.condicao = JSON.stringify(condicoes);
                        } catch (e) {
                            console.error("Erro ao atualizar condições:", e);
                        }
                    }
                });
            }

            // Função para atualizar as chaves das condições
            function atualizarChavesCondicoes(condicoes, novoIndice) {
                if (typeof condicoes === 'object') {
                    const novasCondicoes = {};
                    for (let chave in condicoes) {
                        if (condicoes.hasOwnProperty(chave)) {
                            let novaChave = chave.replace(/\d+/, novoIndice);
                            novasCondicoes[novaChave] = condicoes[chave];
                        }
                    }
                    return novasCondicoes;
                }
                return condicoes;
            }

            // Adicionar formulários
            if (quantidadeDesejada > quantidadeAtual) {
                for (let i = quantidadeAtual; i < quantidadeDesejada; i++) {
                    const newForm = forms[0].cloneNode(true);
                    atualizarFormulario(newForm, i);

                    // Limpar valores
                    newForm.querySelectorAll('input, select, textarea').forEach(input => {
                        input.value = '';
                        if (input.type === 'checkbox') input.checked = false;
                    });

                    forms[forms.length - 1].after(newForm);
                }
            }
            // Remover formulários
            else if (quantidadeDesejada < quantidadeAtual) {
                for (let i = quantidadeAtual - 1; i >= quantidadeDesejada; i--) {
                    forms[i].remove();
                }
            }

            // Reindexar todos os formulários restantes
            formset.querySelectorAll('.formset-form').forEach((form, index) => {
                atualizarFormulario(form, index);
            });

            totalForms.value = quantidadeDesejada;
        });
    });

    // Executar verificação inicial
    setTimeout(() => {
        // Coloque aqui qualquer lógica de verificação inicial necessária
    }, 1000);
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
        console.log(data);

        try {
            const response = await api.post(lastSegment, data); // Envia como dados de formulário

            console.log(response);

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