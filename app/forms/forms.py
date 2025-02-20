import json

def gerar_formulario(parsed_data):
    form_html = ''
    js_code = '''
    <script>
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
    </script>

    '''

    for nome, campo in parsed_data.items():
        if not campo.get('form', False):
            continue  

        descricao = campo['descricao']
        tipo = campo['tipo']
        requerido = 'required' if campo['requerido'] else ''
        condicoes = campo.get('condicao', {})
        condicao_attr = f' data-condicao=\'{json.dumps(condicoes, ensure_ascii=False)}\'' if condicoes else ''

        if tipo == 'string':
            form_html += f'''
            <div class="form-group" id="campo_{nome}"{condicao_attr}>
                <label for="{nome}">{descricao}:</label>
                <input type="text" id="{nome}" name="{nome}" {requerido}>
            </div>
            '''
        elif tipo == 'number':
            form_html += f'''
            <div class="form-group" id="campo_{nome}"{condicao_attr}>
                <label for="{nome}">{descricao}:</label>
                <input type="number" id="{nome}" name="{nome}" placeholder="0" {requerido}>
            </div>
            '''
        elif tipo == 'email':
            form_html += f'''
            <div class="form-group" id="campo_{nome}"{condicao_attr}>
                <label for="{nome}">{descricao}:</label>
                <input type="email" id="{nome}" name="{nome}" placeholder="prime.soho@primesoho.com.br" {requerido}>
            </div>
            '''
        elif tipo == 'date':
            form_html += f'''
            <div class="form-group" id="campo_{nome}"{condicao_attr}>
                <label for="{nome}">{descricao}:</label>
                <input type="date" id="{nome}" name="{nome}" {requerido}>
            </div>
            '''
        elif tipo == 'phone':
            form_html += f'''
            <div class="form-group" id="campo_{nome}"{condicao_attr}>
                <label for="{nome}">{descricao}:</label>
                <input type="tel" id="{nome}" name="{nome}" pattern="\\(\\d{{2}}\\) \\d{{5}}-\\d{{4}}" placeholder="(XX) XXXXX-XXXX" {requerido}>
            </div>
            '''
        elif tipo == 'cpf':
            form_html += f'''
            <div class="form-group" id="campo_{nome}"{condicao_attr}>
                <label for="{nome}">{descricao}:</label>
                <input type="text" id="{nome}" name="{nome}" pattern="\\d{{3}}\\.\\d{{3}}\\.\\d{{3}}-\\d{{2}}" placeholder="XXX.XXX.XXX-XX" {requerido}>
            </div>
            '''
        elif tipo == 'select' and 'variaveis' in campo and campo['variaveis']:
            options = ''.join([f'<option value="{var}">{var}</option>' for var in campo['variaveis']])
            form_html += f'''
            <div class="form-group" id="campo_{nome}"{condicao_attr}>
                <label for="{nome}">{descricao}:</label>
                <select id="{nome}" name="{nome}" {requerido}>
                    {options}
                </select>
            </div>
            '''
        elif tipo == 'textarea':
            form_html += f'''
            <div class="form-group" id="campo_{nome}"{condicao_attr}>
                <label for="{nome}">{descricao}:</label>
                <textarea id="{nome}" name="{nome}" {requerido}></textarea>
            </div>
            '''
        elif tipo == 'checkbox':
            form_html += f'''
            <div class="form-group" id="campo_{nome}"{condicao_attr}>
                <label for="{nome}">{descricao}:</label>
                <input type="checkbox" id="{nome}" name="{nome}" {requerido}>
            </div>
            '''

    form_html += '''
    <div class="form-group">
        <button type="submit">Enviar</button>
    </div>
    '''

    return form_html, js_code
