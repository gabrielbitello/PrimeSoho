def gerar_formulario(parsed_data):
    form_html = ''
    
    for campo in parsed_data:
        nome = campo['nome']
        descricao = campo['descricao']
        tipo = campo['tipo']
        requerido = 'required' if campo['requerido'] else ''
        
        # Verificando o tipo e criando o campo adequado
        if tipo == 'string':
            form_html += f'''
            <div class="form-group">
                <label for="{nome}">{descricao}:</label>
                <input type="text" id="{nome}" name="{nome}" {requerido}>
            </div>
            '''
        elif tipo == 'number':
            form_html += f'''
            <div class="form-group">
                <label for="{nome}">{descricao}:</label>
                <input type="number" id="{nome}" name="{nome}" {requerido}>
            </div>
            '''
        elif tipo == 'select' and 'variaveis' in campo:
            options = ''.join([f'<option value="{var}">{var}</option>' for var in campo['variaveis']])
            form_html += f'''
            <div class="form-group">
                <label for="{nome}">{descricao}:</label>
                <select id="{nome}" name="{nome}" {requerido}>
                    {options}
                </select>
            </div>
            '''
    
    # Botão de envio
    form_html += '''
    <div class="form-group">
        <button type="submit">Enviar</button>
    </div>
    '''
    
    return form_html
