
import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .utils.yaml_receiver import load_yaml, parse_yaml, parse_yaml_options
from .utils.docx_generator import gen_docx
from django.contrib.auth.decorators import login_required
from .forms import DynamicForm, create_formsets
from .utils.extra_tempalte import opcoes_generator
import json

from django import forms
from django.forms import formset_factory

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
    parsed_data_options = parse_yaml_options(yaml_data)
    
    # Separar campos independentes dos campos agrupados
    independent_fields = {nome: campo for nome, campo in parsed_data.items() 
                            if not campo.get('grupo')}
    
    # Obter todos os grupos únicos presentes nos campos
    grupos_unicos = set(campo.get('grupo') for nome, campo in parsed_data.items() 
                        if campo.get('grupo'))
    
    # Organizar campos por grupo
    grouped_fields = {}
    for grupo in grupos_unicos:
        grouped_fields[grupo] = {nome: campo for nome, campo in parsed_data.items() 
                                if campo.get('grupo') == grupo}
    
    # Inicializar forms e formsets
    independent_form = None
    formsets = {}
    
    if request.method == 'POST':
        # Processar dados do POST
        independent_form = DynamicForm(independent_fields, request.POST)
        
        # Processar os formsets
        valid_formsets = True
        formsets_data = {}
        
        for grupo, campos_grupo in grouped_fields.items():
            # Criar o FormSet específico para este grupo
            GroupFormSet = formset_factory(
                create_group_form_class(campos_grupo), 
                extra=1
            )
            
            # Instanciar o formset com os dados do POST
            formset = GroupFormSet(
                request.POST, 
                prefix=f'grupo_{grupo}'  # Importante: usar um prefixo para evitar conflitos de nomes
            )
            
            formsets[grupo] = formset
            
            # Validar o formset
            if formset.is_valid():
                formsets_data[grupo] = [form.cleaned_data for form in formset]
            else:
                valid_formsets = False
                break  # Interrompe se algum formset for inválido
        
        # Validar o formulário principal e todos os formsets
        if independent_form.is_valid() and valid_formsets:
            try:
                # Combinar dados do formulário principal e dos formsets
                dados = independent_form.cleaned_data.copy()
                dados.update(formsets_data)
                
                # Gerar o arquivo DOCX
                docx_name = gen_docx(dados, folder, yaml_data)
                
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
        # GET request - criar formulário vazio
        independent_form = DynamicForm(independent_fields)
        
        # Criar formsets vazios para cada grupo
        for grupo, campos_grupo in grouped_fields.items():
            GroupFormSet = formset_factory(
                create_group_form_class(campos_grupo), 
                extra=1
            )
            formsets[grupo] = GroupFormSet()
    
    # Gerar as opções formatadas
    try:
        opcoes_formatadas = opcoes_generator(parsed_data_options)
    except Exception as e:
        return JsonResponse({
            'error': f'Erro ao gerar opções formatadas: {str(e)}'
        }, status=500)
    
    return render(request, 'form.html', {
        'independent_form': independent_form,
        'formsets': formsets,
        'opcoes_formatadas': opcoes_formatadas,
        'folder': folder  # Pode ser útil no template
    })

def create_group_form_class(campos_grupo):
    """
    Cria uma classe de formulário dinâmica para um grupo específico de campos.
    
    Args:
        campos_grupo: Dicionário com campos pertencentes a um grupo específico
        
    Returns:
        Uma classe Form do Django com os campos configurados
    """
    class GroupForm(forms.Form):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Obtém o prefixo do formulário, que inclui o número da cópia
            form_prefix = self.prefix
            
            # Atualiza os widgets com o prefixo correto
            for field_name, field in self.fields.items():
                if hasattr(field.widget, 'attrs'):
                    # Atualiza o ID do widget com o prefixo completo
                    field.widget.attrs['id'] = f"{form_prefix}-{field_name}"
                    
                    # Atualiza as condições se existirem
                    if 'data-condicao' in field.widget.attrs and field.widget.attrs['data-condicao']:
                        condicoes = json.loads(field.widget.attrs['data-condicao'])
                        condicoes_ajustadas = {}
                        
                        # Cria o novo prefixo para as condições (mantendo apenas o número do formulário)
                        # Ex: de 'grupo_clientes-0' para 'form-0-'
                        if form_prefix and '-' in form_prefix:
                            numero_form = form_prefix.split('-')[-1]
                            novo_prefixo = f"form-{numero_form}-"
                            
                            for campo, valor in condicoes.items():
                                # Remove qualquer prefixo anterior (caso exista)
                                if '-' in campo:
                                    campo_base = campo.split('-')[-1]
                                else:
                                    campo_base = campo
                                    
                                campo_ajustado = f"{novo_prefixo}{campo_base}"
                                condicoes_ajustadas[campo_ajustado] = valor
                            
                            # Atualiza o atributo com as condições ajustadas
                            field.widget.attrs['data-condicao'] = json.dumps(condicoes_ajustadas, ensure_ascii=False)
    
    # Adiciona campos ao formulário do grupo
    for nome, campo_info in campos_grupo.items():
        # Converte as informações do campo em um campo Django real
        field = create_django_field(nome, campo_info)
        if field:
            GroupForm.base_fields[nome] = field
    
    return GroupForm

def create_django_field(nome, campo_info):
    """
    Converte dados do campo em um objeto Field do Django.
    
    Args:
        nome: Nome do campo
        campo_info: Dicionário com informações do campo
        
    Returns:
        Um objeto Field do Django configurado
    """
    if not campo_info.get('form', False):
        return None
        
    descricao = campo_info['descricao']
    tipo = campo_info['tipo']
    requerido = campo_info['requerido']
    condicoes = campo_info.get('condicao', {})
    
    # Converte as condições para JSON (se existirem)
    # Não aplicamos prefixo aqui, isso será feito no __init__ do GroupForm
    condicao_attr = json.dumps(condicoes, ensure_ascii=False) if condicoes else ''
    
    # Atributos do widget para o campo
    widget_attrs = {
        'class': 'form-control',
        'placeholder': '',
        'data-condicao': condicao_attr
    }
    
    # Criação do campo de acordo com o tipo
    if tipo == 'string':
        return forms.CharField(label=descricao, required=requerido, 
                                widget=forms.TextInput(attrs=widget_attrs))
    elif tipo == 'number':
        widget_attrs['placeholder'] = '0'
        return forms.IntegerField(label=descricao, required=requerido, 
                                    widget=forms.NumberInput(attrs=widget_attrs))
    elif tipo == 'email':
        widget_attrs['placeholder'] = 'example@domain.com'
        widget_attrs['class'] += ' email'
        return forms.EmailField(label=descricao, required=requerido, 
                                widget=forms.EmailInput(attrs=widget_attrs))
    elif tipo == 'date':
        return forms.DateField(label=descricao, required=requerido, 
                                widget=forms.DateInput(attrs=widget_attrs))
    elif tipo == 'phone':
        widget_attrs['placeholder'] = '+55 (41) 90000-0000'
        widget_attrs['class'] += ' phone'
        return forms.CharField(label=descricao, required=requerido, 
                                widget=forms.TextInput(attrs=widget_attrs))
    elif tipo == 'cpf':
        widget_attrs['placeholder'] = '000.000.000-00'
        widget_attrs['class'] += ' cpf'
        return forms.CharField(label=descricao, required=requerido, 
                                widget=forms.TextInput(attrs=widget_attrs))
    elif tipo == 'select' and 'variaveis' in campo_info:
        choices = [(var, var) for var in campo_info['variaveis']]
        return forms.ChoiceField(label=descricao, required=requerido, 
                                choices=choices, widget=forms.Select(attrs=widget_attrs))
    elif tipo == 'textarea':
        return forms.CharField(label=descricao, required=requerido, 
                                widget=forms.Textarea(attrs=widget_attrs))
    elif tipo == 'checkbox':
        return forms.BooleanField(label=descricao, required=requerido, 
                                    widget=forms.CheckboxInput(attrs=widget_attrs))
    elif tipo == 'datalist' and 'variaveis' in campo_info:
        widget_attrs['list'] = f'opcoes_{nome}'
        return forms.CharField(label=descricao, required=requerido, 
                                widget=forms.TextInput(attrs=widget_attrs))
                                
    
    return None  # Retorna None se o tipo não for reconhecido