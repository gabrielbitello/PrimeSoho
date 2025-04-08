document.addEventListener("DOMContentLoaded", function () {
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

    const form = document.getElementById("dynamicForm");

    // Organize inputs into their respective blocks visually without changing the HTML structure
    function organizeBlocks() {
        const inputs = form.querySelectorAll("[data-block]");
        let currentBlockId = null;
        let blockContainer = null;

        inputs.forEach(input => {
            const blockId = input.dataset.block;
            const formGroup = input.closest(".form-group");

            if (!blockId || !formGroup) return;

            // Check if we need to create a new visual block container
            if (blockId !== currentBlockId) {
                currentBlockId = blockId;

                // Create a new visual block container
                blockContainer = document.createElement("div");
                blockContainer.classList.add("block-container");
                blockContainer.dataset.blockId = blockId;

                // Insert the block container before the first form group of the block
                formGroup.parentNode.insertBefore(blockContainer, formGroup);
            }

            // Append the form group to the current block container visually
            blockContainer.appendChild(formGroup);
        });
    }

    organizeBlocks();

    // Apply conditions to dynamically show/hide fields
    function aplicarCondicoes(elemento) {
        const camposCondicionais = elemento.querySelectorAll('*[data-condicao]');

        camposCondicionais.forEach(campo => {
            const condicoesStr = campo.dataset.condicao;

            if (!condicoesStr) return;

            let condicoes;
            try {
                condicoes = JSON.parse(condicoesStr);
            } catch (e) {
                console.error("Erro ao analisar condição:", e);
                return;
            }

            const campoAtual = campo.id || campo.name || "campo desconhecido"; // Identifica o campo dependente
            const conditionsMet = Array.isArray(condicoes)
                ? condicoes.some(condicao => verificaCondicaoUnica(condicao, campoAtual))
                : Object.entries(condicoes).every(([chave, valor]) => verificaCondicaoUnica({ [chave]: valor }, campoAtual));

            const inputs = campo.matches('input, select, textarea') ? [campo] : campo.querySelectorAll('input, select, textarea');
            const divContainer = campo.closest('div');

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

    function verificaCondicaoUnica(condicao, campoAtual) {
        const [chave, valorEsperado] = Object.entries(condicao)[0];

        if (chave.includes('/')) {
            return chave.split('/').some(parteChave => verificaCampo(parteChave, valorEsperado, campoAtual));
        }

        return verificaCampo(chave, valorEsperado, campoAtual);
    }

    function verificaCampo(chave, valorEsperado, campoAtual) {
        // Tenta encontrar o campo controlador diretamente pelo ID
        let elementoControlador = document.getElementById(chave);

        // Se não encontrar, tenta localizar dentro de formsets (prefixos dinâmicos)
        if (!elementoControlador) {
            const formGroup = document.querySelector(`[data-block-id]`);
            if (formGroup) {
                const formPrefix = formGroup.closest('.formset-form')?.querySelector('[name$="-TOTAL_FORMS"]')?.name.split('-')[0];
                if (formPrefix) {
                    const prefixedKey = `${formPrefix}-${chave}`;
                    elementoControlador = document.getElementById(prefixedKey);
                }
            }
        }

        if (!elementoControlador) {
            console.warn(`Campo dependente "${campoAtual}" não encontrou o controlador "${chave}".`);
            return false; // Retorna false se o campo controlador não existir
        }

        if (elementoControlador.type === 'checkbox') {
            return elementoControlador.checked === (valorEsperado === true || valorEsperado === 'true');
        } else {
            const valorAtual = elementoControlador.value.toString().trim().toLowerCase();
            const esperado = Array.isArray(valorEsperado)
                ? valorEsperado.map(val => val.toString().trim().toLowerCase())
                : [valorEsperado.toString().trim().toLowerCase()];
            return esperado.includes(valorAtual);
        }
    }

    // Add listeners to dynamically added fields
    function adicionarOuvintes(elemento) {
        elemento.querySelectorAll('input, select, textarea').forEach(el => {
            el.addEventListener('change', () => aplicarCondicoes(form));
        });
    }

    // MutationObserver to handle dynamically added elements
    const observer = new MutationObserver(mutationsList => {
        for (const mutation of mutationsList) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        aplicarCondicoes(node);
                        adicionarOuvintes(node);
                    }
                });
            }
        }
    });

    observer.observe(form, { childList: true, subtree: true });

    // Initial application of conditions
    aplicarCondicoes(form);
    adicionarOuvintes(form);

    // Fix formfactory functionality for dynamically added forms
    document.querySelectorAll('.multiplicador-btn').forEach(button => {
        button.addEventListener('click', function () {
            const grupo = this.dataset.grupo;
            const inputQuantidade = document.getElementById(`${grupo}-quantidade`);
            if (!inputQuantidade) {
                console.error(`Input de quantidade não encontrado para o grupo "${grupo}"`);
                return;
            }

            const quantidadeDesejada = Math.max(1, parseInt(inputQuantidade.value) || 1);
            const grupoCampos = document.querySelector(`.grupo-campos[data-grupo="${grupo}"]`);
            if (!grupoCampos) {
                console.error(`Grupo de campos não encontrado para o grupo "${grupo}"`);
                return;
            }

            const formset = grupoCampos.querySelector('.formset');
            if (!formset) {
                console.error(`Formset não encontrado para o grupo "${grupo}"`);
                return;
            }

            const forms = formset.querySelectorAll('.formset-form');
            const totalForms = grupoCampos.querySelector('[name$="-TOTAL_FORMS"]');
            if (!totalForms) {
                console.error(`Campo TOTAL_FORMS não encontrado para o grupo "${grupo}"`);
                return;
            }

            const quantidadeAtual = forms.length;

            // Add or remove forms based on the desired quantity
            if (quantidadeDesejada > quantidadeAtual) {
                for (let i = quantidadeAtual; i < quantidadeDesejada; i++) {
                    const newForm = forms[0].cloneNode(true);

                    // Clear input values and reset attributes
                    newForm.querySelectorAll('input, select, textarea').forEach(input => {
                        input.value = '';
                        if (input.type === 'checkbox') input.checked = false;

                        // Update the name and id attributes to avoid conflicts
                        const nameAttr = input.getAttribute('name');
                        if (nameAttr) {
                            const newName = nameAttr.replace(/\d+/, i);
                            input.setAttribute('name', newName);
                        }

                        const idAttr = input.getAttribute('id');
                        if (idAttr) {
                            const newId = idAttr.replace(/\d+/, i);
                            input.setAttribute('id', newId);
                        }
                    });

                    formset.appendChild(newForm);
                }
            } else if (quantidadeDesejada < quantidadeAtual) {
                for (let i = quantidadeAtual - 1; i >= quantidadeDesejada; i--) {
                    forms[i].remove();
                }
            }

            // Update the total forms count
            totalForms.value = quantidadeDesejada;

            // Reapply conditions and listeners to the new forms
            aplicarCondicoes(formset);
            adicionarOuvintes(formset);
        });
    });
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