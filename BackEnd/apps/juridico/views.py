
import os
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from .utils.forms import gerar_formulario
from .utils.yaml_receiver import load_yaml, parse_yaml
from .utils.docx_generator import gen_docx

# Obtém o diretório onde o arquivo views.py está localizado
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define o caminho para o diretório 'docs' no mesmo diretório que o arquivo views.py
docs_path = os.path.join(current_dir, 'docs')

def listar_formularios(request):

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
    return render(request, 'form_hub.html', {'formularios': formularios})

def formulario(request, folder):
    # Caminho da pasta onde os YAMLs estão localizados
    yaml_file_path = os.path.join(docs_path, folder, f'{folder}.yaml')
    
    # Verificar se o arquivo YAML existe
    if not os.path.exists(yaml_file_path):
        return HttpResponse("Arquivo YAML não encontrado.", status=404)
    
    # Carregar o arquivo YAML
    yaml_data = load_yaml(yaml_file_path)

    if not yaml_data:
        return HttpResponse("Erro ao carregar o arquivo YAML.", status=500)
    
    # Processar os dados do YAML
    parsed_data = parse_yaml(yaml_data)

    if request.method == 'POST':
        form_data = request.POST
        # Agora você pode usar os dados do formulário para gerar o DOCX
        dados = {nome: form_data.get(nome) for nome, campo in parsed_data.items()}

        # Gerar o arquivo DOCX com os dados coletados
        caminho_saida = gen_docx(dados, folder, yaml_data)

        # Enviar o arquivo gerado para o cliente
        with open(caminho_saida, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response['Content-Disposition'] = f'attachment; filename={folder}_preenchido.docx'
            return response
    
    # Gerar o formulário dinâmico com base nos dados do YAML
    form_html, js_code = gerar_formulario(parsed_data)  # Recebe ambos: HTML e JS
    
    # Passa o HTML do formulário e o código JS para o template
    return render(request, 'form.html', {'form_html': form_html, 'js_code': js_code})


