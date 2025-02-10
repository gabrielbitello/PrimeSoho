from jinja2 import Template

def gerar_formulario(parsed_data):
    """
    Gera o HTML do formulário com base nos dados do YAML.
    """
    form_html = ''
    
    for campo, config in parsed_data.items():
        # Verificar se o campo tem a chave 'form' como True (indica que deve aparecer no formulário)
        if config['form']:
            # Abrir a div do campo
            form_html += f'<div class="form-group" id="{campo}">\n'
            
            # Adicionar o label do campo
            form_html += f'<label for="{campo}">{config["descricao"]}</label>\n'
            
            # Gerar o input de acordo com o tipo
            if config['tipo'] == 'string':
                form_html += f'<input type="text" id="{campo}" name="{campo}"'
                if config['requerido']:
                    form_html += ' required'
                form_html += '>\n'
                
            elif config['tipo'] == 'number':
                form_html += f'<input type="number" id="{campo}" name="{campo}"'
                if config['requerido']:
                    form_html += ' required'
                # Adicionar restrições de regras
                if 'min' in config['regras']:
                    form_html += f' min="{config["regras"]["min"]}"'
                if 'max' in config['regras']:
                    form_html += f' max="{config["regras"]["max"]}"'
                form_html += '>\n'
                
            elif config['tipo'] == 'string' and len(config['variaveis']) > 0:
                # Para campos com variáveis, como "Pagamento"
                form_html += f'<select id="{campo}" name="{campo}">\n'
                for op in config['variaveis']:
                    form_html += f'<option value="{op}">{op}</option>\n'
                form_html += '</select>\n'
            
            # Fechar a div do campo
            form_html += '</div>\n'
    
    # Incluir o botão de envio
    form_html += '<div class="form-group">\n'
    form_html += '<button type="submit">Enviar</button>\n'
    form_html += '</div>\n'

    return form_html

# Testando o HTML com um exemplo
if __name__ == "__main__":
    yaml_data = load_yaml('exemplo.yaml')
    if yaml_data and validate_yaml(yaml_data):
        parsed_data = parse_yaml(yaml_data)
        
        # Gerar o HTML
        form_html = gerar_formulario(parsed_data)
        print(form_html)
