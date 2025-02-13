import os
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, send_file
from .forms import gerar_formulario
from app.utils.yaml_receiver import load_yaml, parse_yaml
from app.utils.docx_generator import gen_docx

bp = Blueprint('forms', __name__)

@bp.route('/formulario', methods=['GET'])
def listar_formularios():
    # Caminho para a pasta de documentos
    docs_path = os.path.abspath(os.path.join('app', 'docs'))
    
    # Lista de formulários disponíveis
    formularios = []
    
    # Percorre as pastas dentro de 'docs' para encontrar os arquivos YAML
    for folder in os.listdir(docs_path):
        folder_path = os.path.join(docs_path, folder)
        if os.path.isdir(folder_path):
            yaml_file = os.path.join(folder_path, f'{folder}.yaml')
            if os.path.exists(yaml_file):
                formularios.append(folder)
    
    # Renderiza a página com a lista de formulários
    return render_template('form_hub.html', formularios=formularios)


# Rota para exibir o formulário baseado no YAML
@bp.route('/formulario/<folder>', methods=['GET', 'POST'])
def formulario(folder):
    # Caminho da pasta onde os YAMLs estão localizados
    yaml_file_path = os.path.abspath(os.path.join('app', 'docs', folder, f'{folder}.yaml'))
    
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
        # Agora você pode usar os dados do formulário para gerar o DOCX
        dados = {nome: form_data.get(nome) for nome, campo in parsed_data.items()}

        # Gerar o arquivo DOCX com os dados coletados
        caminho_saida = gen_docx(dados, folder, yaml_data)

        # Enviar o arquivo gerado para o cliente
        return send_file(caminho_saida, as_attachment=True, download_name=f'{folder}_preenchido.docx')
    
    # Gerar o formulário dinâmico com base nos dados do YAML
    form_html, js_code = gerar_formulario(parsed_data)  # Recebe ambos: HTML e JS
    
    # Passa o HTML do formulário e o código JS para o template
    return render_template('form.html', form_html=form_html, js_code=js_code)

@bp.route('/log', methods=['POST'])
def receber_log():
    log_data = request.get_json()
    log = log_data.get('log')
    # Aqui você pode armazenar os logs no banco de dados ou fazer o que quiser com eles
    print(f"Log recebido: {log}")
    return jsonify({'status': 'sucesso'}), 200