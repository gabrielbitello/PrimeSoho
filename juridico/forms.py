from django import forms
from django.forms import formset_factory
import json
from django.utils import timezone

class DynamicForm(forms.Form):
    datalist_html = ""

    def __init__(self, parsed_data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Para campos independentes (sem grupo)
        for nome, campo in parsed_data.items():
            if not campo.get('form', False) or campo.get('grupo', ''):
                continue  # Ignora campos sem a chave 'form' ou com grupo

            # Criar campo normal
            field = self.create_field(nome, campo)
            if field:
                self.fields[nome] = field

    @classmethod
    def create_field(cls, nome, campo):
        """
        Cria um campo do formulário com base nas informações fornecidas.
        """
        if not campo.get('form', False):
            return None
            
        descricao = campo['descricao']
        tipo = campo['tipo']
        requerido = campo['requerido']
        condicoes = campo.get('condicao', {})
        grupo = campo.get('grupo', '')

        # Converte as condições para JSON (se existirem)
        condicao_attr = json.dumps(condicoes, ensure_ascii=False) if condicoes else ''

        # Atributos do widget para o campo
        widget_attrs = {
            'id': nome,
            'class': 'form-control',
            'placeholder': '',
            'list': '',
            'data-condicao': condicao_attr,
            'data-grupo': grupo,
        }

        # Criação do campo de acordo com o tipo
        field = None
        datalist_html = ""
        
        if tipo == 'string':
            field = forms.CharField(label=descricao, required=requerido, widget=forms.TextInput(attrs=widget_attrs))
        elif tipo == 'number':
            widget_attrs['placeholder'] += '0'
            widget_attrs['class'] += ' number'
            field = forms.CharField(label=descricao, required=requerido, widget=forms.TextInput(attrs=widget_attrs))
        elif tipo == 'email':
            widget_attrs['placeholder'] += 'example@domain.com'
            widget_attrs['class'] += ' email'
            field = forms.EmailField(label=descricao, required=requerido, widget=forms.EmailInput(attrs=widget_attrs))
        elif tipo == 'date':
            curent_date = timezone.localdate()
            widget_attrs['type'] = 'date'
            widget_attrs['value'] = curent_date
            field = forms.DateField(label=descricao, required=requerido, widget=forms.DateInput(attrs=widget_attrs))
        elif tipo == 'phone':
            widget_attrs['placeholder'] += '+55 (00) 90000-0000'
            widget_attrs['class'] += ' phone'
            field = forms.CharField(label=descricao, required=requerido, widget=forms.TextInput(attrs=widget_attrs))
        elif tipo == 'cpf':
            widget_attrs['placeholder'] += '000.000.000-00'
            widget_attrs['class'] += ' cpf'
            field = forms.CharField(label=descricao, required=requerido, widget=forms.TextInput(attrs=widget_attrs))
        elif tipo == 'select' and 'variaveis' in campo:
            choices = [(var, var) for var in campo['variaveis']]
            field = forms.ChoiceField(label=descricao, required=requerido, choices=choices, widget=forms.Select(attrs=widget_attrs))
        elif tipo == 'textarea':
            field = forms.CharField(label=descricao, required=requerido, widget=forms.Textarea(attrs=widget_attrs))
        elif tipo == 'checkbox':
            field = forms.BooleanField(label=descricao, required=requerido, widget=forms.CheckboxInput(attrs=widget_attrs))
        elif tipo == 'datalist' and 'variaveis' in campo:
            widget_attrs['list'] += f'opcoes_{nome}'
            field = forms.CharField(label=descricao, required=requerido, widget=forms.TextInput(attrs=widget_attrs))
            
            datalist_html = f'<datalist id="opcoes_{nome}">'
            for opcao in campo['variaveis']:
                datalist_html += f'<option value="{opcao}">'
            datalist_html += '</datalist>'
            cls.datalist_html += datalist_html  # Acumula HTML dos datalists

        return field

    @classmethod
    def get_datalist_html(cls):
        """Retorna o HTML completo dos datalists gerados."""
        return cls.datalist_html


def create_group_form_class(campos_grupo):
    """
    Cria uma classe de formulário dinâmica para um grupo específico de campos.
    """
    class GroupForm(forms.Form):
        datalist_html = ""
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Obtém o prefixo do formulário, que inclui o número da cópia
            form_prefix = self.prefix
            
            # Atualiza os widgets com o prefixo correto
            for field_name, field in self.fields.items():
                if hasattr(field.widget, 'attrs'):
                    # Atualiza o ID do widget com o prefixo completo
                    field.widget.attrs['id'] = f"{form_prefix}-{field_name}" if form_prefix else field_name
                    
                    # Atualiza as condições se existirem
                    if 'data-condicao' in field.widget.attrs and field.widget.attrs['data-condicao']:
                        condicoes = json.loads(field.widget.attrs['data-condicao'])
                        condicoes_ajustadas = {}
                        
                        # Cria o novo prefixo para as condições (mantendo apenas o número do formulário)
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
        if not campo_info.get('form', False):
            continue
            
        field = DynamicForm.create_field(nome, campo_info)
        if field:
            GroupForm.base_fields[nome] = field
    
    return GroupForm


def get_form_and_formsets(parsed_data, request_data=None, request_files=None):
    """
    Função auxiliar para criar formulário principal e formsets.
    
    Args:
        parsed_data: Dicionário com todos os campos parseados
        request_data: Dados da requisição POST (opcional)
        request_files: Arquivos da requisição (opcional)
        
    Returns:
        Uma tupla (form, formsets) com o formulário principal e os formsets configurados
    """
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
    
    # Inicializar o formulário principal
    independent_form = None
    
    if request_data:
        independent_form = DynamicForm(independent_fields, request_data, request_files)
    else:
        independent_form = DynamicForm(independent_fields)
    
    # Inicializar formsets
    formsets = {}
    
    for grupo, campos_grupo in grouped_fields.items():
        # Criar o FormSet específico para este grupo
        GroupFormSet = formset_factory(
            create_group_form_class(campos_grupo),
            extra=1
        )
        
        # Instanciar o formset com ou sem dados do POST
        if request_data:
            formsets[grupo] = GroupFormSet(
                request_data,
            )
        else:
            formsets[grupo] = GroupFormSet()
    
    return independent_form, formsets


def validate_forms(independent_form, formsets):
    """
    Valida o formulário principal e todos os formsets.
    Se um campo obrigatório não for enviado, ele é ignorado.
    Se for enviado em branco, a validação falha.

    Args:
        independent_form: O formulário principal
        formsets: Dicionário com os formsets

    Returns:
        (is_valid, dados_combinados, errors)
    """
    raw_data = independent_form.data

    # Desativa obrigatoriedade de campos não enviados
    for field_name, field in independent_form.fields.items():
        if field.required:
            if field_name not in raw_data:
                field.required = False
            else:
                value = raw_data.get(field_name)
                if value in [None, '', [], {}]:
                    return False, None, {field_name: ["Este campo é obrigatório e não pode estar em branco."]}

    # Valida o form principal
    if not independent_form.is_valid():
        return False, None, independent_form.errors

    
    formsets_data = {}
    for grupo, formset in formsets.items():
        for i, form in enumerate(formset.forms):
            raw_form_data = form.data

            for field_name, field in form.fields.items():
                if field.required:
                    key = form.add_prefix(field_name)
                    if key not in raw_form_data:
                        field.required = False
                    else:
                        value = raw_form_data.get(key)
                        if value in [None, '', [], {}]:
                            return False, None, {
                                "grupo": grupo,
                                "form_index": i,
                                "field": field_name,
                                "error": "Este campo é obrigatório e não pode estar em branco."
                            }

        if not formset.is_valid():
            return False, None, {"grupo": grupo, "errors": formset.errors}

        formsets_data[grupo] = [form.cleaned_data for form in formset]

    dados_combinados = independent_form.cleaned_data.copy()
    dados_combinados.update(formsets_data)

    return True, dados_combinados, None
