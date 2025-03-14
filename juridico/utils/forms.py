import json

def gerar_formulario(parsed_data):
    form_html = ''

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
                <input type="email" id="{nome}" name="{nome}" class="email" placeholder="prime.soho@primesoho.com.br" {requerido}>
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
                <input type="tel" id="{nome}" name="{nome}" class="phone" placeholder="+55 (XX) XXXXX-XXXX" {requerido}>
            </div>
            '''
        elif tipo == 'cpf':
            form_html += f'''
            <div class="form-group" id="campo_{nome}"{condicao_attr}>
                <label for="{nome}">{descricao}:</label>
                <input type="text" id="{nome}" name="{nome}" class="cpf" placeholder="XXX.XXX.XXX-XX" {requerido}>
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

    return form_html
