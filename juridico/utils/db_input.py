from django.db import transaction
from django.http import JsonResponse
from django.db.models import fields, ForeignKey
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal
import re

# Importe seus modelos aqui
from clientes.models import Cliente, Uniao
from imoveis.models import Imoveis, Proposta
# Importe outros modelos conforme necessário

# Dicionário para mapear nomes de tabelas para classes de modelo
MODEL_MAP = {
    'proprietario': Cliente,
    'Imovel': Imoveis,
    'Uniao': Uniao,
    'Proposta': Proposta,
    # Adicione outros mapeamentos conforme necessário
}

def save_form_data(form_data, config):
    print(f"Iniciando save_form_data com config: {config}")
    print(f"Form data: {form_data}")

    try:
        with transaction.atomic():
            instances = {}
            for table in config['db_table']:
                instances[table['nome']] = save_table_data(form_data, table, instances)
            
            # Processar regras adicionais para todas as instâncias salvas
            for table in config['db_table']:
                for instance in instances[table['nome']]:
                    process_additional_rules(instance, form_data, table, instances)
                    
        return JsonResponse({'success': True})
    except Exception as e:
        print(f"Erro geral em save_form_data: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})
    
def save_table_data(form_data, table_config, instances):
    """
    Salva os dados de uma tabela específica.
    """
    print(f"Processando tabela: {table_config['nome']}")
    
    model_class = MODEL_MAP.get(table_config['nome'])
    if not model_class:
        print(f"Modelo não encontrado para: {table_config['nome']}")
        return None

    if table_config['form-factory']:
        return save_form_factory_data(form_data, table_config, model_class)
    else:
        return save_single_data(form_data, table_config, model_class)

def save_form_factory_data(form_data, table_config, model_class):
    """
    Salva dados para tabelas com form-factory True.
    """
    instances = []
    form_count = get_form_count(form_data)
    
    for i in range(form_count):
        instance_data = {}
        uid_field = None
        uid_value = None
        
        # Processar o campo UID
        if 'uid' in table_config:
            uid_config = table_config['uid']
            uid_parts = uid_config.split(':')
            if len(uid_parts) == 2:
                form_field, db_field = uid_parts
                uid_value = form_data.get(f"form-{i}-{form_field}")
                _, uid_field = db_field.split('/')
        
        for field_name, field_config in table_config['campos'].items():
            try:
                if isinstance(field_config, str):
                    model_name, field = field_config.split('/')
                    form_field_name = f"form-{i}-{field_name}"
                    value = form_data.get(form_field_name)
                    
                    model_field = model_class._meta.get_field(field)
                    converted_value = convert_value(value, model_field)
                    
                    instance_data[field] = converted_value
                elif isinstance(field_config, dict) and 'regra' in field_config:
                    instance_data[field_name] = process_special_field(field_config, form_data, i)
                elif field_config is None:
                    continue
                else:
                    print(f"Configuração de campo não reconhecida para {field_name}: {field_config}")
            except Exception as e:
                print(f"Erro ao processar campo {field_name}: {str(e)}")
        
        try:
            if uid_field and uid_value:
                instance, created = model_class.objects.update_or_create(**{uid_field: uid_value}, defaults=instance_data)
            else:
                instance = model_class.objects.create(**instance_data)
                created = True
            
            action = 'Criado' if created else 'Atualizado'
            print(f"{action} registro {i+1} para {table_config['nome']} com {uid_field or 'ID'}: {uid_value or instance.id}")

            instances.append(instance)
        except Exception as e:
            print(f"Erro ao salvar dados para {table_config['nome']} (registro {i+1}): {str(e)}")
            print(f"Dados que causaram o erro: {instance_data}")
    
    return instances

def save_single_data(form_data, table_config, model_class, form_factory_count=1):
    instances = []
    
    for i in range(form_factory_count):
        instance_data = {}
        uid_field = None
        uid_value = None
        
        # Processar campos regulares
        for field_name, field_config in table_config['campos'].items():
            try:
                if isinstance(field_config, str):
                    model_name, field = field_config.split('/')
                    # Ajuste para lidar com FormFactory
                    value = form_data.get(f"{field_name}_{i}" if form_factory_count > 1 else field_name)
                    
                    model_field = model_class._meta.get_field(field)
                    converted_value = convert_value(value, model_field)
                    
                    instance_data[field] = converted_value
                elif isinstance(field_config, dict) and 'regra' in field_config:
                    # Ajuste para lidar com FormFactory em campos especiais
                    value, field_info = process_special_field(field_config, form_data, i if form_factory_count > 1 else None)
                    if value and field_info:
                        if isinstance(value, dict):
                            for key, val in value.items():
                                model_name, field = field_info[key].split('/')
                                instance_data[field] = val
                        else:
                            model_name, field = field_info.split('/')
                            instance_data[field] = value
                elif field_config is None:
                    continue
                else:
                    print(f"Configuração de campo não reconhecida para {field_name}: {field_config}")
            except Exception as e:
                print(f"Erro ao processar campo {field_name}: {str(e)}")
        
        # Processar o campo UID
        if 'uid' in table_config:
            uid_config = table_config['uid']
            uid_parts = uid_config.split(':')
            if len(uid_parts) == 2:
                form_field, db_field = uid_parts
                # Ajuste para lidar com FormFactory no campo UID
                uid_value = form_data.get(f"{form_field}_{i}" if form_factory_count > 1 else form_field)
                _, uid_field = db_field.split('/')
        
        try:
            with transaction.atomic():
                if uid_field and uid_value:
                    # Tenta encontrar um registro existente com o UID fornecido
                    instance, created = model_class.objects.update_or_create(
                        **{uid_field: uid_value},
                        defaults=instance_data
                    )
                    action = 'Criado' if created else 'Atualizado'
                else:
                    # Se não temos um UID válido, sempre criamos um novo registro
                    instance = model_class.objects.create(**instance_data)
                    action = 'Criado'

                print(f"{action} registro para {table_config['nome']} com {uid_field or 'ID'}: {uid_value or instance.id}")
                
                instances.append(instance)
        except Exception as e:
            print(f"Erro ao salvar dados para {table_config['nome']}: {str(e)}")
            print(f"Dados que causaram o erro: {instance_data}")
    
    return instances

def convert_value(value, model_field):
    if value == '' or value is None:
        return None
    
    try:
        if isinstance(model_field, ForeignKey):
            related_model = model_field.related_model
            
            try:
                return related_model.objects.get(pk=int(value))
            except ValueError:
                if related_model == get_user_model():
                    return get_user_model().objects.get(username=value)
                else:
                    unique_fields = [f.name for f in related_model._meta.fields if f.unique and not f.primary_key]
                    for field in unique_fields:
                        try:
                            return related_model.objects.get(**{field: value})
                        except ObjectDoesNotExist:
                            continue
                    
                    for field in ['nome', 'name']:
                        if hasattr(related_model, field):
                            return related_model.objects.filter(**{field: value}).first()
                    
                    raise ObjectDoesNotExist(f"Não foi possível encontrar {related_model.__name__} com o valor '{value}'")
        
        elif isinstance(model_field, (fields.CharField, fields.TextField)):
            return str(value)
        elif isinstance(model_field, fields.IntegerField):
            # Remove pontos e substitui vírgula por ponto
            cleaned_value = value.replace('.', '').replace(',', '.')
            return int(float(cleaned_value))
        elif isinstance(model_field, (fields.FloatField, fields.DecimalField)):
            # Remove pontos e substitui vírgula por ponto
            cleaned_value = value.replace('.', '').replace(',', '.')
            if isinstance(model_field, fields.DecimalField):
                return Decimal(cleaned_value)
            return float(cleaned_value)
        elif isinstance(model_field, fields.BooleanField):
            if isinstance(value, bool):
                return value
            return value.lower() in ['true', '1', 'yes', 'on', 't']
        elif isinstance(model_field, fields.DateField):
            from datetime import datetime
            return datetime.strptime(value, '%Y-%m-%d').date()
        elif isinstance(model_field, fields.DateTimeField):
            from datetime import datetime
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        else:
            return value
    except ObjectDoesNotExist as e:
        print(f"Erro: Objeto não encontrado - {str(e)}")
        return None
    except Exception as e:
        print(f"Erro ao converter valor '{value}' para o campo {model_field.name}: {str(e)}")
        return None

def process_special_field(field_config, form_data, form_index):
    """
    Processa campos com regras especiais.
    """
    try:
        if 'Identfy?' in field_config['regra']:
            doc_types = field_config['regra'].split('Identfy?')[1].strip().split(', ')
            doc_info = {}
            for doc in doc_types:
                doc_type, field_path = doc.split(': ')
                doc_info[doc_type] = field_path

            value = form_data.get(f"form-{form_index}-Doc_proprietario")
            if value:
                # Remover caracteres não numéricos
                clean_value = re.sub(r'\D', '', value)
                
                # Identificar o tipo de documento
                if len(clean_value) == 11 and is_valid_cpf(clean_value):
                    return f"CPF: {value}", doc_info['CPF']
                elif len(clean_value) == 9:
                    return f"RG: {value}", doc_info['RG']
                elif len(clean_value) == 11:
                    return f"CNH: {value}", doc_info['CNH']
                elif len(clean_value) > 11:
                    return f"Passaporte: {value}", doc_info['Passaporte']
            
        elif 'Endereco?' in field_config['regra']:
            endereco_config = field_config['regra'].split('Endereco?')[1].strip().split(', ')
            endereco_info = {part.split(': ')[0]: part.split(': ')[1] for part in endereco_config}
            
            endereco_completo = form_data.get(f"form-{form_index}-Endereco_proprietario", '')
            parts = endereco_completo.split(',')
            
            result = {}
            if len(parts) >= 1:
                result['endereco'] = parts[0].strip()
            if len(parts) >= 2:
                result['numero'] = parts[1].strip()
            if len(parts) >= 3:
                result['complemento'] = ', '.join(parts[2:]).strip()
            
            return result, endereco_info

    except Exception as e:
        print(f"Erro ao processar campo especial: {str(e)}")
    return None, None

def is_valid_cpf(cpf):
    # Implementar a lógica de validação de CPF aqui
    # Esta é uma implementação simplificada e não deve ser usada em produção
    if len(cpf) != 11:
        return False
    if cpf == cpf[0] * 11:
        return False
    return True

def get_form_count(form_data):
    """
    Determina o número de formulários no formset.
    """
    try:
        return max([int(key.split('-')[1]) for key in form_data.keys() if key.startswith('form-') and key.split('-')[1].isdigit()]) + 1
    except Exception as e:
        print(f"Erro ao determinar o número de formulários: {str(e)}")
        return 0

def get_inserted_ids(table_name, instances):
    """
    Retorna os IDs dos registros inseridos para uma tabela específica.
    
    :param table_name: Nome da tabela no YAML (ex: "proprietario")
    :param instances: Dicionário contendo as instâncias salvas
    :return: Lista de IDs dos registros inseridos
    """
    if table_name in instances:
        return [instance.id for instance in instances[table_name] if instance.id is not None]
    return []

def process_additional_rules(instance, form_data, table_config, instances):
    """
    Processa regras adicionais para a instância salva.
    """
    for rule in table_config.get('regra', []):
        print(f"Processando regra adicional: {rule['nome']}")
        print(f"Regra: {rule}")
        try:
            if rule['nome'] == 'uniao':
                estado_civil = form_data.get('form-0-Estado_Civil')
                if estado_civil in rule['condicao'][0]['Estado_Civil']:
                    process_uniao(instance, form_data, instances)
            elif rule['nome'] == 'get_inserted_ids':
                if 'campos' in rule and len(rule['campos']) == 2:
                    source_table = rule['campos'][0]
                    target_field = rule['campos'][1]
                    
                    inserted_ids = [inst.id for inst in instances.get(source_table, [])]
                    print(f"IDs inseridos para {source_table}: {inserted_ids}")
                    
                    target_table, target_column = target_field.split('/')
                    if table_config['nome'] == target_table:
                        if hasattr(instance, target_column):
                            field = getattr(instance, target_column)
                            if hasattr(field, 'add'):  # ManyToManyField
                                field.add(*inserted_ids)
                            elif hasattr(field, 'set'):  # ForeignKey
                                if inserted_ids:
                                    field.set(inserted_ids)  # Define todos os IDs para ForeignKey

                    # Salvar a instância após a atualização
                    instance.save()
        except Exception as e:
            print(f"Erro ao processar regra adicional {rule['nome']}: {str(e)}")

def process_uniao(instance, form_data, instances):
    """
    Processa a regra de união/casamento.
    """
    try:
        # Verifica se o estado civil atual está na lista de condições
        estado_civil_atual = instance.estado_civil
        if estado_civil_atual not in ["União Estável", "Casado"]:
            return  # Se não estiver, não processa

        # Obtém todos os clientes processados nesta leva
        clientes_processados = instances.get('proprietario', [])
        
        # Encontra o parceiro potencial (cliente anterior com estado civil compatível)
        parceiro = None
        for cliente in reversed(clientes_processados):
            if cliente.id != instance.id and cliente.estado_civil in ["União Estável", "Casado"]:
                parceiro = cliente
                break

        if parceiro:
            # Verifica se já existe uma união para qualquer um dos clientes
            uniao_existente = Uniao.objects.filter(cliente1__in=[instance, parceiro]) | \
                                Uniao.objects.filter(cliente2__in=[instance, parceiro])

            if not uniao_existente.exists():
                # Cria uma nova união
                with transaction.atomic():
                    nova_uniao = Uniao(
                        cliente1=parceiro,
                        cliente2=instance,
                        data_uniao=form_data.get(f'form-{instances["proprietario"].index(instance)}-Data_Casamento'),
                        regime_uniao=form_data.get(f'form-{instances["proprietario"].index(instance)}-Regime_Casamento')
                    )
                    nova_uniao.save()
            else:
                print(f"União já existe para o cliente {instance.id} ou {parceiro.id}")
        else:
            print(f"Nenhum parceiro encontrado para o cliente {instance.id}")

    except Exception as e:
        print(f"Erro ao processar união: {str(e)}")