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

            // Verifica se as condições são atendidas
            let conditionsMet = false;
            
            // Detecta o formato da condição e aplica a verificação apropriada
            if (Array.isArray(condicoes)) {
                // Formato antigo: array de condições (qualquer uma atendida é suficiente)
                conditionsMet = condicoes.some(condicao => verificaCondicaoUnica(condicao, campoAtual));
            } else if (typeof condicoes === 'object') {
                // Verifica se há condições de formset
                const formsetKeys = Object.keys(condicoes).filter(key => key.startsWith('formset:'));
                
                if (formsetKeys.length > 0) {
                    // Há condições de formset
                    conditionsMet = formsetKeys.every(key => {
                        return verificaCondicaoFormset(key, condicoes[key], campoAtual);
                    });
                    
                    // Verifica também as condições regulares, se houver
                    const regularKeys = Object.keys(condicoes).filter(key => !key.startsWith('formset:'));
                    if (regularKeys.length > 0) {
                        conditionsMet = conditionsMet && regularKeys.every(key => 
                            verificaCondicaoUnica({ [key]: condicoes[key] }, campoAtual));
                    }
                } else {
                    // Formato antigo: objeto de condições (todas devem ser atendidas)
                    conditionsMet = Object.entries(condicoes).every(([chave, valor]) => 
                        verificaCondicaoUnica({ [chave]: valor }, campoAtual));
                }
            }

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

    // Função para encontrar campos de formset
    function findFormsetFields(fieldName) {
        
        // Busca por elementos com id ou name que corresponda ao padrão form-X-fieldName
        const fields = [];
        
        // Busca por id
        document.querySelectorAll(`[id^="form-"][id$="-${fieldName}"]`).forEach(el => {
            fields.push(el);
        });
        
        // Busca por name (caso o id não esteja definido)
        document.querySelectorAll(`[name^="form-"][name$="-${fieldName}"]`).forEach(el => {
            if (!fields.includes(el)) {
                fields.push(el);
            }
        });
        
        return fields;
    }

    // Verifica condições de formset
    function verificaCondicaoFormset(chave, valor, campoAtual) {
        
        const parts = chave.split(':');
        
        if (parts.length < 2) {
            console.warn(`Formato inválido para condição de formset: ${chave}`);
            return false;
        }
        
        const fieldName = parts[1];
        const operator = parts.length >= 3 ? parts[2] : 'any';
        
        // Encontra todos os campos do formset
        const formsetFields = findFormsetFields(fieldName);
        
        if (formsetFields.length === 0) {
            console.warn(`Nenhum campo de formset encontrado para: ${fieldName}`);
            return false;
        }
        
        // Obtém os valores dos campos
        const fieldValues = formsetFields.map(field => field.value);
        
        // Aplica o operador correto
        switch (operator) {
            case 'any':
                // Verifica se qualquer campo tem o valor esperado
                if (Array.isArray(valor)) {
                    const result = fieldValues.some(fv => valor.some(v => 
                        v.toString().trim().toLowerCase() === fv.toString().trim().toLowerCase()
                    ));
                    return result;
                } else if (typeof valor === 'object' && valor !== null) {
                    // Para o caso de combination como {valor1: 1, valor2: 1}
                    return Object.entries(valor).every(([val, minCount]) => {
                        // Normaliza os valores para comparação
                        const normalizedVal = val.toString().trim().toLowerCase();
                        const normalizedFieldValues = fieldValues.map(fv => fv.toString().trim().toLowerCase());
                        
                        const actualCount = normalizedFieldValues.filter(fv => fv === normalizedVal).length;
                        const result = actualCount >= minCount;
                        return result;
                    });
                } else {
                    // Normaliza os valores para comparação
                    const normalizedValue = valor.toString().trim().toLowerCase();
                    const normalizedFieldValues = fieldValues.map(fv => fv.toString().trim().toLowerCase());
                    
                    const result = normalizedFieldValues.includes(normalizedValue);
                    return result;
                }
            
            case 'all':
                // Verifica se todos os campos têm o valor esperado
                if (Array.isArray(valor)) {
                    // Normaliza os valores para comparação
                    const normalizedValues = valor.map(v => v.toString().trim().toLowerCase());
                    const normalizedFieldValues = fieldValues.map(fv => fv.toString().trim().toLowerCase());
                    
                    return normalizedFieldValues.every(fv => normalizedValues.includes(fv));
                } else {
                    // Normaliza os valores para comparação
                    const normalizedValue = valor.toString().trim().toLowerCase();
                    const normalizedFieldValues = fieldValues.map(fv => fv.toString().trim().toLowerCase());
                    
                    return normalizedFieldValues.every(fv => fv === normalizedValue);
                }
            
            case 'equal':
                // Verifica se todos os campos têm o mesmo valor
                if (fieldValues.length === 0) return valor === true;
                
                // Normaliza os valores para comparação
                const normalizedFieldValues = fieldValues.map(fv => fv.toString().trim().toLowerCase());
                const firstValue = normalizedFieldValues[0];
                
                return (normalizedFieldValues.every(fv => fv === firstValue)) === valor;
            
            case 'combination':
                // Verifica combinações específicas de valores
                if (typeof valor !== 'object' || valor === null) return false;
                
                return Object.entries(valor).every(([val, minCount]) => {
                    // Normaliza os valores para comparação
                    const normalizedVal = val.toString().trim().toLowerCase();
                    const normalizedFieldValues = fieldValues.map(fv => fv.toString().trim().toLowerCase());
                    
                    const actualCount = normalizedFieldValues.filter(fv => fv === normalizedVal).length;
                    const result = actualCount >= minCount;
                    return result;
                });
            
            case 'count':
                // Verifica contagem de campos com valores específicos
                if (typeof valor === 'object' && valor !== null) {
                    return Object.entries(valor).every(([val, count]) => {
                        // Normaliza os valores para comparação
                        const normalizedVal = val.toString().trim().toLowerCase();
                        const normalizedFieldValues = fieldValues.map(fv => fv.toString().trim().toLowerCase());
                        
                        const actualCount = normalizedFieldValues.filter(fv => fv === normalizedVal).length;
                        return actualCount >= count;
                    });
                } else {
                    // Conta campos com qualquer valor não vazio
                    const actualCount = fieldValues.filter(fv => fv).length;
                    return actualCount >= parseInt(valor);
                }
            
            default:
                console.warn(`Operador de formset desconhecido: ${operator}`);
                return false;
        }
    }

    function verificaCondicaoUnica(condicao, campoAtual) {
        const [chave, valorEsperado] = Object.entries(condicao)[0];

        if (chave.includes('/')) {
            return chave.split('/').some(parteChave => verificaCampo(parteChave, valorEsperado, campoAtual));
        }

        return verificaCampo(chave, valorEsperado, campoAtual);
    }

    function verificaCampo(chave, valorEsperado, campoAtual) {
        // Se a chave começar com "formset:", delegamos para a função de verificação de formset
        if (chave.startsWith('formset:')) {
            return verificaCondicaoFormset(chave, valorEsperado, campoAtual);
        }
        
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

        // Tenta encontrar pelo nome do campo
        if (!elementoControlador) {
            elementoControlador = document.querySelector(`[name="${chave}"]`);
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