
import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from .utils.forms import gerar_formulario
from .utils.yaml_receiver import load_yaml, parse_yaml
from .utils.docx_generator import gen_docx
from django.contrib.auth.decorators import login_required

# Obtém o diretório onde o arquivo views.py está localizado
current_dir = os.path.dirname(os.path.abspath(__file__))

@login_required(login_url='/login/')
def j_home(request):
    return render(request, 'j_home.html')

@login_required(login_url='/login/')
def listar_formularios(request):

    # Lista de formulários disponíveis
    formularios = []
    
    # Percorre as pastas dentro de 'docs' para encontrar os arquivos YAML
    for folder in os.listdir(os.path.join(current_dir, 'docs')):
        folder_path = os.path.join(os.path.join(current_dir, 'docs'), folder)
        if os.path.isdir(folder_path):
            yaml_file = os.path.join(folder_path, f'{folder}.yaml')
            if os.path.exists(yaml_file):
                formularios.append(folder)
    
    # Renderiza a página com a lista de formulários
    return render(request, 'form_hub.html', {'formularios': formularios})

@login_required(login_url='/login/')
def formulario(request, folder):
    # Caminho da pasta onde os YAMLs estão localizados
    yaml_file_path = os.path.join(os.path.join(current_dir, 'docs'), folder, f'{folder}.yaml')
    
    # Verificar se o arquivo YAML existe
    if not os.path.exists(yaml_file_path):
        return JsonResponse({"error": "Arquivo YAML não encontrado."}, status=404)
    
    # Carregar o arquivo YAML
    yaml_data = load_yaml(yaml_file_path)

    if not yaml_data:
        return JsonResponse({"error": "Erro ao carregar o arquivo YAML."}, status=500)
    
    # Processar os dados do YAML
    parsed_data = parse_yaml(yaml_data)

    if request.method == 'POST':
        try:
            form_data = request.POST
            # Agora você pode usar os dados do formulário para gerar o DOCX
            dados = {nome: form_data.get(nome) for nome, campo in parsed_data.items()}

            # Gerar o arquivo DOCX com os dados coletados
            docx_name = gen_docx(dados, folder, yaml_data)

            # Verifica se o arquivo foi gerado corretamente
            if os.path.exists(os.path.join(current_dir, 'output', docx_name)):
                
                if not os.path.exists(os.path.join(current_dir, 'output', docx_name)):
                    return JsonResponse({"error": "Erro ao gerar o arquivo DOCX."}, status=500)

                # Retornar a URL do arquivo gerado para o frontend
                file_url = os.path.join('/output/', docx_name)  # Caminho relativo para o arquivo
                return JsonResponse({'message': 'O arquivo DOCX foi gerado com sucesso!', 'file_url': file_url})
            else:
                return JsonResponse({"error": "Erro ao gerar o arquivo DOCX."}, status=500)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    # Gerar o formulário dinâmico com base nos dados do YAML
    form_html = gerar_formulario(parsed_data)  # Recebe ambos: HTML e JS
    
    # Passa o HTML do formulário e o código JS para o template
    return render(request, 'form.html', {'form_html': form_html})
