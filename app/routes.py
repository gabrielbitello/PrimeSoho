import os
import yaml
from flask import Blueprint, render_template, request, redirect, url_for
from .forms import gerar_formulario

bp = Blueprint('main', __name__)

# Função para carregar o arquivo YAML
def load_yaml(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Erro ao carregar YAML: {e}")
        return None

# Função para processar as condições complexas
def processar_condicao(condicao):
    if condicao.get('tipo') == 'regex':
        return {'tipo': 'regex', 'valor': condicao.get('valor')}
    elif condicao.get('tipo') == 'menor_que':
        return {'tipo': 'menor_que', 'valor': condicao.get('valor')}
    # Adicione mais tipos conforme sua necessidade
    return {}

# Função para processar variáveis
def processar_variaveis(variaveis):
    return variaveis  # Pode ser expandido conforme necessário

# Função para processar regras
def processar_regras(regras):
    return regras  # Pode ser expandido conforme necessário

# Função para analisar o YAML e retornar os dados estruturados
def parse_yaml(data):
    documentos = data.get('Documentos', {}).get('Documentos-Config', [])
    parsed_data = {}

    for item in documentos:
        nome = item.get('nome')
        if nome:
            parsed_data[nome] = {
                'tipo': item.get('tipo'),
                'descricao': item.get('descricao', ''),
                'requerido': item.get('requerido', False),
                'condicao': processar_condicao(item.get('condicao', {})),
                'variaveis': processar_variaveis(item.get('variaveis', [])),
                'regras': processar_regras(item.get('regras', {})),
                'grupo': item.get('grupo', ''),
                'outras_informacoes': item.get('outras_informacoes', {}),
                'valores_possiveis': item.get('valores_possiveis', [])
            }
    return parsed_data

# Rota para exibir o formulário baseado no YAML
@bp.route('/formulario/<folder>', methods=['GET', 'POST'])
def formulario(folder):
    # Caminho da pasta onde os YAMLs estão localizados
    yaml_file_path = os.path.join('docs', folder, f'{folder}.yaml')
    
    # Verificar se o arquivo YAML existe
    if not os.path.exists(yaml_file_path):
        return "Arquivo YAML não encontrado.", 404
    
    # Carregar o arquivo YAML
    yaml_data = load_yaml(yaml_file_path)

    if not yaml_data:
        return "Erro ao carregar o arquivo YAML.", 500
    
    # Processar os dados do YAML
    parsed_data = parse_yaml(yaml_data)

    if request.method == 'POST':
        form_data = request.form
        # Aqui você pode processar os dados do formulário conforme a necessidade
        print(form_data)
        return redirect(url_for('main.formulario', folder=folder))
    
    # Gerar o formulário dinâmico com base nos dados do YAML
    form_html = gerar_formulario(parsed_data)
    
    return render_template('form.html', form_html=form_html)
