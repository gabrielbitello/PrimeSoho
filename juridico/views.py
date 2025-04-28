
import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .utils.yaml_receiver import load_yaml, parse_yaml, multiplicador_yaml_options, options_yaml_options
from .utils.docx_generator import generate_docx
from django.contrib.auth.decorators import login_required
from .forms import DynamicForm, get_form_and_formsets, validate_forms
from .utils.db_input import save_form_data

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
    yaml_file_path = os.path.join(current_dir, 'docs', folder, f'{folder}.yaml')
    
    if not os.path.exists(yaml_file_path):
        return JsonResponse({"error": "Arquivo YAML não encontrado."}, status=404)
        
    yaml_data = load_yaml(yaml_file_path)
    
    if not yaml_data:
        return JsonResponse({"error": "Erro ao carregar o arquivo YAML."}, status=500)
        
    parsed_data = parse_yaml(yaml_data)
    multiplicador_data_options = multiplicador_yaml_options(yaml_data)
    
    if request.method == 'POST':
        # Usar a função auxiliar para criar formulário e formsets
        independent_form, formsets, all_datalists = get_form_and_formsets(parsed_data, request.POST, request.FILES)
        
        # Validar formulário e formsets
        is_valid, dados_combinados, errors = validate_forms(independent_form, formsets)

        config_yaml = options_yaml_options(yaml_data)
        
        if not is_valid:
            print (errors)
            return JsonResponse({
                'error': 'Por favor, preencha todos os campos obrigatórios corretamente.',
                'errors': errors
            }, status=400)
            
        try:
            # Gerar o arquivo DOCX
            try:
                docx_name = generate_docx(dados_combinados, folder, yaml_data, multiplicador_data_options)
                print (docx_name)
                if config_yaml.get('db', False):
                    save_form_data(dados_combinados, config_yaml)
            except Exception as e:
                return JsonResponse({
                    'error': f'Erro ao gerar o arquivo DOCX: {str(e)}'
                }, status=500)

            if os.path.exists(os.path.join(current_dir, 'output', docx_name)):
                file_url = os.path.join('/j/output/', docx_name)
                return JsonResponse({
                    'message': 'O arquivo DOCX foi gerado com sucesso!',
                    'file_url': file_url
                })
            else:
                return JsonResponse({"error": "Erro ao gerar o arquivo DOCX."}, status=500)
        except Exception as e:
            return JsonResponse({
                'error': f'Erro durante o processamento do formulário: {str(e)}'
            }, status=500)
    else:
        # Requisição GET - criar formulário e formsets vazios
        independent_form, formsets, all_datalists = get_form_and_formsets(parsed_data)

    return render(request, 'form.html', {
        'independent_form': independent_form,
        'formsets': formsets,
        'all_datalists': all_datalists  
    })