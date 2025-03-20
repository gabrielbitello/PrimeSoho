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
        console.log('=== INÍCIO DA VERIFICAÇÃO DE CONDIÇÕES ===');
        // Seleciona todos os elementos com data-condicao dentro de main
        let camposCondicionais = document.querySelectorAll('main *[data-condicao]');
        
        console.log(`Encontrados ${camposCondicionais.length} campos condicionais`);
        
        camposCondicionais.forEach((campo, index) => {
            console.log(`\n--- Analisando campo #${index + 1} ---`);
            
            let condicoesStr = campo.dataset.condicao;

            console.log('Condição (string):', condicoesStr);
            
            let condicoes;
            try {
                condicoes = JSON.parse(condicoesStr); // Parse do JSON
                console.log('Condição (objeto):', condicoes);
            } catch (e) {
                console.error('Erro ao analisar JSON:', e);
                return; // Se ocorrer erro ao analisar, ignore o campo
            }

            let conditionsMet = true;

            // Caso as condições estejam em formato de objeto, converta para uma lista simplificada
            if (typeof condicoes === 'object' && !Array.isArray(condicoes)) {
                console.log('Convertendo objeto para array de condições');
                condicoes = Object.entries(condicoes).map(([chave, valor]) => {
                    console.log(`  Convertendo: ${chave} => ${JSON.stringify(valor)}`);
                    return { [chave]: valor };
                });
                console.log('Condições após conversão:', condicoes);
            }

            // Agora, vamos manipular as condições com base no novo formato
            conditionsMet = condicoes.some((condicao, condIndex) => {
                console.log(`\nVerificando condição #${condIndex + 1}:`, condicao);
            
                // Obter todas as chaves do objeto
                let chaves = Object.keys(condicao);
                console.log('Chaves encontradas:', chaves);
                
                // Verifica se a condição é uma string e contém '/'
                if (chaves.some(chave => chave.includes('/'))) {
                    console.log('Detectada condição com "/"');
            
                    // Para cada chave que contém '/', divida a chave e extraia o que está antes da barra
                    let resultadoCondicao = chaves.some(chave => {
                        console.log(`\nProcessando chave com '/': ${chave}`);
                        let partesChave = chave.split('/'); // Divida a chave na barra
                        console.log('Partes da chave:', partesChave);
            
                        // Agora, vamos processar cada parte da chave
                        return partesChave.some((parteChave, index) => {
                            console.log(`Verificando parte ${index + 1}: ${parteChave}`);
                            
                            // Pegue o valor esperado da condição para cada parte da chave
                            let valorEsperado = condicao[chave].toString().trim().toLowerCase(); 
                            console.log(`Valor esperado: "${valorEsperado}"`);
            
                            // Verifica se o campo realmente existe no DOM
                            let elementoControlador = document.getElementById(parteChave);
                            if (!elementoControlador) {
                                console.log(`ERRO: Elemento #${parteChave} não encontrado no DOM`);
                                return false; // Retorna falso se o campo não for encontrado
                            }
                            
                            // Verifica se é um checkbox para usar a propriedade checked
                            if (elementoControlador.type === 'checkbox') {
                                let isChecked = elementoControlador.checked;
                                let isExpectedChecked = (valorEsperado === 'true');
                                console.log(`Checkbox #${parteChave}: atual=${isChecked}, esperado=${isExpectedChecked}`);
                                return isChecked === isExpectedChecked;
                            } else {
                                // Obtém o valor do campo para outros tipos de input
                                let valorAtual = elementoControlador.value.toString().trim().toLowerCase();
                                console.log(`Campo #${parteChave}: atual="${valorAtual}", esperado="${valorEsperado}"`);
                        
                                // Comparar o valor atual com o valor esperado
                                let resultado = valorAtual === valorEsperado;
                                console.log(`Comparação: ${resultado ? 'APROVADA' : 'REPROVADA'}`);
                                return resultado;
                            }
                        });
                    });
            
                    console.log(`Resultado final da condição com '/': ${resultadoCondicao ? 'APROVADA' : 'REPROVADA'}`);
                    return resultadoCondicao;
                }
            
                // Caso contrário, se for uma condição simples de campo-valor
                let [chave, valorEsperado] = Object.entries(condicao)[0];
                console.log(`Condição simples: #${chave} = ${JSON.stringify(valorEsperado)}`);
                
                let elementoControlador = document.getElementById(chave);

                if (!elementoControlador) {
                    console.log(`ERRO: Elemento #${chave} não encontrado no DOM`);
                    return false;
                }

                // Verifica se é um checkbox para usar a propriedade checked
                if (elementoControlador.type === 'checkbox') {
                    let isChecked = elementoControlador.checked;
                    let isExpectedChecked = (valorEsperado === true || valorEsperado === 'true');
                    console.log(`Checkbox #${chave}: atual=${isChecked}, esperado=${isExpectedChecked}`);
                    let resultado = isChecked === isExpectedChecked;
                    console.log(`Comparação: ${resultado ? 'APROVADA' : 'REPROVADA'}`);
                    return resultado;
                } else {
                    let valorAtual = elementoControlador.value.toString().trim().toLowerCase();
                    console.log(`Campo #${chave}: atual="${valorAtual}"`);
                    
                    let esperado = Array.isArray(valorEsperado) ? 
                        valorEsperado.map(val => val.toString().trim().toLowerCase()) : 
                        [valorEsperado.toString().trim().toLowerCase()];
                    
                    console.log(`Valores esperados:`, esperado);

                    let resultado = esperado.includes(valorAtual);
                    console.log(`Comparação: ${resultado ? 'APROVADA' : 'REPROVADA'}`);
                    return resultado;
                }
            });

            console.log(`\nResultado final para o campo: ${conditionsMet ? 'APROVADA' : 'REPROVADA'}`);

            // Agora verificamos a div que contém tanto o campo quanto o label
            let divContainer = campo.closest('div');
            let label = divContainer ? divContainer.querySelector('label') : null;

            if (conditionsMet) {
                // Exibe o campo e o label
                console.log('Exibindo o campo e o label');
                campo.style.display = "block";
                if (label) label.style.display = "block"; // Mostra o label se a condição for atendida
                
                let input = campo.querySelector('input, select, textarea, datalist, checkbox');
                if (input) {
                    console.log('Habilitando o input');
                    input.disabled = false;
                }
            } else {
                // Esconde o campo e o label
                console.log('Escondendo o campo e o label');
                campo.style.display = "none";
                if (label) label.style.display = "none"; // Esconde o label também
                
                let input = campo.querySelector('input, select, textarea, datalist, checkbox');
                if (input) {
                    console.log('Desabilitando o input');
                    input.disabled = true;
                }
            }
        });
        
        console.log('=== FIM DA VERIFICAÇÃO DE CONDIÇÕES ===\n');
    }

    // Ouvinte de evento para campos de input, select, checkbox, etc.
    document.querySelectorAll('input, select, textarea, checkbox, datalist').forEach(elemento => {
        elemento.addEventListener('change', verificarCondicoes);
    });

    // Executa a verificação inicial
    console.log('Executando verificação inicial');
    verificarCondicoes();
});







// Função executada quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    // Código original para adicionar item
    document.querySelectorAll('.adicionar-item').forEach(function(button) {
        button.addEventListener('click', function() {
            const grupo = this.getAttribute('data-grupo');
            
            // Solução: Usar um seletor mais específico
            const formset = document.querySelector(`div[data-grupo="${grupo}"]`);
            
            // Verificar se o formset existe antes de tentar acessá-lo
            if (!formset) {
                console.error(`Formset para grupo "${grupo}" não encontrado`);
                return; // Sair da função se o formset não for encontrado
            }
            
            const forms = formset.querySelectorAll('.formset-form');
            if (forms.length === 0) {
                console.error(`Nenhum formulário encontrado no formset do grupo "${grupo}"`);
                return;
            }
            
            const totalForms = formset.querySelector('[name$="-TOTAL_FORMS"]');
            if (!totalForms) {
                console.error(`Campo de total de formulários não encontrado para o grupo "${grupo}"`);
                return;
            }
            
            // Clonar o último formulário
            const newForm = forms[forms.length - 1].cloneNode(true);
            
            // Atualizar os índices nos IDs e names
            const formRegex = new RegExp(`(\\d+)-`, 'g');
            const newIndex = parseInt(totalForms.value);
            
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
            
            // Atualizar o contador total de formulários
            totalForms.value = newIndex + 1;
        });
    });
    
    // NOVO CÓDIGO: Gerenciar cópias baseado no valor do input
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