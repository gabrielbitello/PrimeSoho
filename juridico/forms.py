from django import forms
from django.forms import formset_factory
import json

class DynamicForm(forms.Form):
    datalist_html = ""


    def __init__(self, parsed_data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.groups = {}  # Dicionário para armazenar grupos de campos

        # Itera sobre os dados recebidos para gerar os campos do formulário
        for nome, campo in parsed_data.items():
            if not campo.get('form', False):
                continue  # Ignora campos sem a chave 'form'

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
                'data-grupo': grupo,  # Melhor usar como atributo de dados
            }

            # Criação do campo de acordo com o tipo
            field = None
            if tipo == 'string':
                field = forms.CharField(label=descricao, required=requerido, widget=forms.TextInput(attrs=widget_attrs))
            elif tipo == 'number':
                widget_attrs['placeholder'] += '0'
                field = forms.IntegerField(label=descricao, required=requerido, widget=forms.NumberInput(attrs=widget_attrs))
            elif tipo == 'email':
                widget_attrs['placeholder'] += 'example@domain.com'
                widget_attrs['class'] += ' email'
                field = forms.EmailField(label=descricao, required=requerido, widget=forms.EmailInput(attrs=widget_attrs))
            elif tipo == 'date':
                field = forms.DateField(label=descricao, required=requerido, widget=forms.DateInput(attrs=widget_attrs))
            elif tipo == 'phone':
                widget_attrs['placeholder'] += '+55 (41) 90000-0000'
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
                DynamicForm.datalist_html += datalist_html  # Acumula HTML dos datalists

            # Verifica se o campo é válido antes de adicioná-lo
            if isinstance(field, forms.Field):
                if grupo:
                    # Se o campo tiver um grupo, adiciona ao grupo correspondente
                    if grupo not in self.groups:
                        self.groups[grupo] = []
                    self.groups[grupo].append((nome, field))  # Armazena o nome do campo junto com o campo
                else:
                    # Campos sem grupo são adicionados diretamente
                    self.fields[nome] = field

        # Adiciona os campos dos grupos ao formulário
        for grupo, campos in self.groups.items():
            for nome_campo, campo in campos:
                # Adiciona cada campo com seu nome original (não o nome do grupo)
                self.fields[nome_campo] = campo

    @classmethod
    def get_datalist_html(cls):
        """Retorna o HTML completo dos datalists gerados."""
        return cls.datalist_html
    
    def get_grouped_fields(self):
        """
        Retorna um dicionário com campos agrupados para uso no template.
        """
        return self.groups


def create_formsets(parsed_data):
    """
    Função para criar formsets para os grupos de campos.
    """
    formsets = {}
    
    # Primeiro, organize os campos por grupo
    campos_por_grupo = {}
    
    for nome, campo in parsed_data.items():
        if not campo.get('form', False):
            continue
            
        grupo = campo.get('grupo', '')
        if grupo:
            if grupo not in campos_por_grupo:
                campos_por_grupo[grupo] = {}
            campos_por_grupo[grupo][nome] = campo
    
    # Para cada grupo de campos, cria-se um formset
    for grupo, campos_grupo in campos_por_grupo.items():
        if campos_grupo:
            # Criar uma nova classe de formulário para o grupo
            class GroupForm(forms.Form):
                pass

            # Adiciona dinamicamente os campos ao formulário do grupo
            for nome, campo_info in campos_grupo.items():
                # Aqui você precisará converter o dicionário campo_info em um Field do Django
                # similar ao que você faz na classe DynamicForm
                field = convert_dict_to_field(nome, campo_info)
                if field:
                    GroupForm.base_fields[nome] = field

            # Cria o formset para o grupo
            formsets[grupo] = formset_factory(GroupForm, extra=1)
    
    return formsets

def convert_dict_to_field(nome, campo_info):
    """
    Converte um dicionário de informações de campo em um objeto Field do Django.
    Esta função deve implementar a mesma lógica que você tem na classe DynamicForm.
    """
    descricao = campo_info['descricao']
    tipo = campo_info['tipo']
    requerido = campo_info['requerido']
    
    widget_attrs = {
        'id': nome,
        'class': 'form-control',
        'placeholder': '',
    }
    
    # Implemente a mesma lógica que você tem na classe DynamicForm
    # para criar campos baseados no tipo
    if tipo == 'string':
        return forms.CharField(label=descricao, required=requerido, widget=forms.TextInput(attrs=widget_attrs))
    elif tipo == 'number':
        widget_attrs['placeholder'] = '0'
        return forms.IntegerField(label=descricao, required=requerido, widget=forms.NumberInput(attrs=widget_attrs))
    # Adicione outros tipos conforme necessário...
    
    return None  # Retorna None se o tipo não for reconhecido