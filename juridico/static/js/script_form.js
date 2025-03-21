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
        
        camposCondicionais.forEach((campo) => {
            let condicoesStr = campo.dataset.condicao;

            if (!condicoesStr) {
                return;
            }
            
            let condicoes;
            try {
                condicoes = JSON.parse(condicoesStr); // Parse do JSON
            } catch (e) {
                console.error("Erro ao analisar condição:", e);
                return; // Se ocorrer erro ao analisar, ignore o campo
            }

            // Caso as condições estejam em formato de objeto, converta para uma lista simplificada
            if (typeof condicoes === 'object' && !Array.isArray(condicoes)) {
                condicoes = Object.entries(condicoes).map(([chave, valor]) => {
                    return { [chave]: valor };
                });
            }

            // Verifica se alguma das condições é atendida
            let conditionsMet = condicoes.some((condicao) => {
                // Obter todas as chaves do objeto
                let chaves = Object.keys(condicao);
                
                // Verifica se a condição é uma string e contém '/'
                if (chaves.some(chave => chave.includes('/'))) {
                    // Para cada chave que contém '/', divida a chave e extraia o que está antes da barra
                    return chaves.some(chave => {
                        let partesChave = chave.split('/'); // Divida a chave na barra
            
                        // Agora, vamos processar cada parte da chave
                        return partesChave.some((parteChave) => {
                            // Pegue o valor esperado da condição para cada parte da chave
                            let valorEsperado = condicao[chave].toString().trim().toLowerCase(); 
            
                            // Verifica se o campo realmente existe no DOM
                            let elementoControlador = document.getElementById(parteChave);
                            if (!elementoControlador) {
                                console.warn(`Campo controlador não encontrado: ${parteChave}`);
                                return false; // Retorna falso se o campo não for encontrado
                            }
                            
                            // Verifica se é um checkbox para usar a propriedade checked
                            if (elementoControlador.type === 'checkbox') {
                                let isChecked = elementoControlador.checked;
                                let isExpectedChecked = (valorEsperado === 'true');
                                return isChecked === isExpectedChecked;
                            } else {
                                // Obtém o valor do campo para outros tipos de input
                                let valorAtual = elementoControlador.value.toString().trim().toLowerCase();
                                return valorAtual === valorEsperado;
                            }
                        });
                    });
                }
            
                // Caso contrário, se for uma condição simples de campo-valor
                let [chave, valorEsperado] = Object.entries(condicao)[0];
                
                let elementoControlador = document.getElementById(chave);

                if (!elementoControlador) {
                    console.warn(`Campo controlador não encontrado: ${chave}`);
                    return false;
                }

                // Verifica se é um checkbox para usar a propriedade checked
                if (elementoControlador.type === 'checkbox') {
                    let isChecked = elementoControlador.checked;
                    let isExpectedChecked = (valorEsperado === true || valorEsperado === 'true');
                    return isChecked === isExpectedChecked;
                } else {
                    let valorAtual = elementoControlador.value.toString().trim().toLowerCase();
                    
                    let esperado = Array.isArray(valorEsperado) ? 
                        valorEsperado.map(val => val.toString().trim().toLowerCase()) : 
                        [valorEsperado.toString().trim().toLowerCase()];
                    
                    return esperado.includes(valorAtual);
                }
            });

            // CORREÇÃO: Verificar se o próprio elemento é um input ou contém inputs
            // Se campo for um input, label, select, etc., encontre o input diretamente
            let inputs;
            if (campo.tagName === 'INPUT' || campo.tagName === 'SELECT' || campo.tagName === 'TEXTAREA') {
                inputs = [campo];
            } else {
                // Se for uma div ou outro contêiner, procure inputs dentro dele
                inputs = campo.querySelectorAll('input, select, textarea');
            }

            if (conditionsMet) {
                // Exibe o campo
                campo.style.display = "block";
                
                // Ativa todos os inputs dentro do campo
                inputs.forEach(input => {
                    input.disabled = false;
                    console.log(`Habilitando campo: ${input.id || input.name}`);
                });
                
                // Se o campo estiver dentro de um div com label, exibe o label também
                let divContainer = campo.closest('div');
                if (divContainer) {
                    let labels = divContainer.querySelectorAll('label');
                    labels.forEach(label => {
                        label.style.display = "block";
                    });
                }
            } else {
                // Esconde o campo
                campo.style.display = "none";
                
                // Desativa todos os inputs dentro do campo
                inputs.forEach(input => {
                    input.disabled = true;
                    console.log(`Desabilitando campo: ${input.id || input.name}`);
                });
                
                // Se o campo estiver dentro de um div com label, esconde o label também
                let divContainer = campo.closest('div');
                if (divContainer) {
                    let labels = divContainer.querySelectorAll('label');
                    labels.forEach(label => {
                        label.style.display = "none";
                    });
                }
            }
        });
    }

    // Adiciona logs para verificar se a função está sendo executada
    console.log("Script de condições carregado");

    // Ouvinte de evento para campos de input, select, checkbox, etc.
    document.querySelectorAll('input, select, textarea').forEach(elemento => {
        elemento.addEventListener('change', function() {
            console.log(`Campo alterado: ${elemento.id || elemento.name}`);
            verificarCondicoes();
        });
    });

    // Executa a verificação inicial
    console.log("Executando verificação inicial de condições");
    verificarCondicoes();
});







// Função executada quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    // Gerenciar cópias baseado no valor do input
    document.querySelectorAll('.multiplicador').forEach(function(button) {
        button.addEventListener('click', function() {
            // Pegar o ID do botão
            const buttonId = this.id;
            
            // Procurar input com o mesmo ID
            const inputQuantidade = document.getElementById(buttonId);
            if (!inputQuantidade) {
                console.error(`Input com ID "${buttonId}" não encontrado`);
                return;
            }
            
            // Obter o valor do input (garantir que seja pelo menos 1)
            let quantidadeDesejada = parseInt(inputQuantidade.value);
            if (isNaN(quantidadeDesejada) || quantidadeDesejada < 1) {
                quantidadeDesejada = 1;
                inputQuantidade.value = "1";
            }
            
            // Identificar o grupo de formulários relacionado
            const grupo = this.getAttribute('data-grupo');
            if (!grupo) {
                console.error("Botão não possui atributo data-grupo");
                return;
            }
            
            // Localizar o formset
            const formset = document.querySelector(`div[data-grupo="${grupo}"]`);
            if (!formset) {
                console.error(`Formset para grupo "${grupo}" não encontrado`);
                return;
            }
            
            // Contar quantas cópias existem atualmente
            const forms = formset.querySelectorAll('.formset-form');
            const quantidadeAtual = forms.length;
            
            // Campo para atualizar o total de formulários
            const totalForms = formset.querySelector('[name$="-TOTAL_FORMS"]');
            if (!totalForms) {
                console.error(`Campo de total de formulários não encontrado para o grupo "${grupo}"`);
                return;
            }
            
            // Se precisamos adicionar mais cópias
            if (quantidadeDesejada > quantidadeAtual) {
                for (let i = quantidadeAtual; i < quantidadeDesejada; i++) {
                    // Clonar o primeiro formulário como modelo
                    const newForm = forms[0].cloneNode(true);
                    
                    // Atualizar os índices nos IDs e names
                    const formRegex = new RegExp(`(\\d+)-`, 'g');
                    const newIndex = i;
                    
                    newForm.innerHTML = newForm.innerHTML.replace(formRegex, `${newIndex}-`);
                    
                    // Limpar os valores dos campos
                    newForm.querySelectorAll('input, select, textarea').forEach(function(input) {
                        input.value = '';
                        if (input.type === 'checkbox') {
                            input.checked = false;
                        }
                    });
                    
                    // Adicionar o novo formulário ao formset
                    forms[forms.length - 1].after(newForm);
                }
            }
            // Se precisamos remover cópias
            else if (quantidadeDesejada < quantidadeAtual) {
                // Remover os formulários excedentes, começando do final
                for (let i = quantidadeAtual - 1; i >= quantidadeDesejada; i--) {
                    forms[i].remove();
                }
            }
            
            // Atualizar o contador total de formulários
            totalForms.value = quantidadeDesejada;
        });
    });
    
    // Função para debug - verificar se os elementos necessários existem
    function verificarElementos() {
        console.log('Botões de adicionar item:', document.querySelectorAll('.adicionar-item').length);
        console.log('Botões de cópia:', document.querySelectorAll('.botao-copia').length);
        
        document.querySelectorAll('.adicionar-item, .botao-copia').forEach(function(button) {
            const grupo = button.getAttribute('data-grupo');
            console.log(`Grupo: ${grupo}, Botão ID: ${button.id}, Classe: ${button.className}`);
            const formset = document.querySelector(`div[data-grupo="${grupo}"]`);
            console.log(`Formset encontrado: ${formset !== null}`);
            if (formset) {
                console.log(`Forms no formset: ${formset.querySelectorAll('.formset-form').length}`);
                console.log(`Total forms field: ${formset.querySelector('[name$="-TOTAL_FORMS"]') !== null}`);
            }
        });
    }
    
    // Executar verificação após carregar a página
    setTimeout(verificarElementos, 1000);
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