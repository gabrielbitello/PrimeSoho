from django import forms
from django.core.exceptions import ValidationError
import json

class DynamicForm(forms.Form):
    def __init__(self, parsed_data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Variáveis para o formulário e os datalists
        self.datalist_html = ""  # Aqui armazenamos o HTML dos datalists
        
        for nome, campo in parsed_data.items():
            if not campo.get('form', False):
                continue

            descricao = campo['descricao']
            tipo = campo['tipo']
            requerido = campo['requerido']
            condicoes = campo.get('condicao', {})
            
            # Atribuindo condicoes ao campo, se existirem
            condicao_attr = json.dumps(condicoes, ensure_ascii=False) if condicoes else ''

            # Adicionar campos dinamicamente
            if tipo == 'string':
                self.fields[nome] = forms.CharField(
                    label=descricao,
                    required=requerido,
                    widget=forms.TextInput(attrs={
                        'id': nome,
                        'class': 'form-control',
                        'data-condicao': condicao_attr,
                    })
                )
            elif tipo == 'number':
                self.fields[nome] = forms.IntegerField(
                    label=descricao,
                    required=requerido,
                    widget=forms.NumberInput(attrs={
                        'id': nome,
                        'class': 'form-control',
                        'data-condicao': condicao_attr,
                        'placeholder': "0"
                    })
                )
            elif tipo == 'email':
                self.fields[nome] = forms.EmailField(
                    label=descricao,
                    required=requerido,
                    widget=forms.EmailInput(attrs={
                        'id': nome,
                        'class': 'form-control email',
                        'data-condicao': condicao_attr,
                        'placeholder': 'prime.soho@primesoho.com.br'
                    })
                )
            elif tipo == 'date':
                self.fields[nome] = forms.DateField(
                    label=descricao,
                    required=requerido,
                    widget=forms.DateInput(attrs={
                        'id': nome,
                        'class': 'form-control',
                        'data-condicao': condicao_attr
                    })
                )
            elif tipo == 'phone':
                self.fields[nome] = forms.CharField(
                    label=descricao,
                    required=requerido,
                    widget=forms.TextInput(attrs={
                        'id': nome,
                        'class': 'form-control phone',
                        'data-condicao': condicao_attr,
                        'placeholder': '+55 (XX) XXXXX-XXXX'
                    })
                )
            elif tipo == 'cpf':
                self.fields[nome] = forms.CharField(
                    label=descricao,
                    required=requerido,
                    widget=forms.TextInput(attrs={
                        'id': nome,
                        'class': 'form-control cpf',
                        'data-condicao': condicao_attr,
                        'placeholder': 'XXX.XXX.XXX-XX'
                    })
                )
            elif tipo == 'select' and 'variaveis' in campo and campo['variaveis']:
                choices = [(var, var) for var in campo['variaveis']]
                self.fields[nome] = forms.ChoiceField(
                    label=descricao,
                    required=requerido,
                    choices=choices,
                    widget=forms.Select(attrs={
                        'id': nome,
                        'class': 'form-control',
                        'data-condicao': condicao_attr
                    })
                )
            elif tipo == 'textarea':
                self.fields[nome] = forms.CharField(
                    label=descricao,
                    required=requerido,
                    widget=forms.Textarea(attrs={
                        'id': nome,
                        'class': 'form-control',
                        'data-condicao': condicao_attr
                    })
                )
            elif tipo == 'checkbox':
                self.fields[nome] = forms.BooleanField(
                    label=descricao,
                    required=requerido,
                    widget=forms.CheckboxInput(attrs={
                        'id': nome,
                        'class': 'form-control',
                        'data-condicao': condicao_attr
                    })
                )
            elif tipo == 'datalist' and 'variaveis' in campo and campo['variaveis']:
                # Campo de texto com sugestão de opções (datalist)
                self.fields[nome] = forms.CharField(
                    label=descricao,
                    required=requerido,
                    widget=forms.TextInput(attrs={
                        'id': nome,
                        'class': 'form-control',
                        'list': f"opcoes_{nome}",  # Liga o input ao datalist
                        'data-condicao': condicao_attr  # Passa a condição associada ao campo
                    })
                )
                
                # Criar o Datalist dinamicamente com as opções
                opcoes = campo['variaveis']  # Aqui você obtém as opções de 'variaveis'
                
                # Gerar o HTML do datalist dentro do formulário
                datalist_html = f'<datalist id="opcoes_{nome}">'
                for opcao in opcoes:
                    datalist_html += f'<option value="{opcao}">'
                datalist_html += '</datalist>'
                
                # Adicionar o HTML do datalist ao contexto (adicionando todos os datalists)
                self.datalist_html += datalist_html  # Concatenar os HTML dos datalists

    def get_datalist_html(self):
        """
        Retorna o HTML completo de todos os datalists gerados.
        """
        return self.datalist_html
