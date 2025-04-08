import yaml

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
    return condicao

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
                'form': item.get('form', True),
                'descricao': item.get('descricao', ''),
                'requerido': item.get('requerido', False),
                'condicao': processar_condicao(item.get('condicao', [])),
                'variaveis': processar_variaveis(item.get('variaveis', [])),
                'regras': processar_regras(item.get('regras', [])),
                'grupo': item.get('grupo', ''),
                'block': item.get('block', ''),  # Include block value
            }
    return parsed_data

def multiplicador_yaml_options(data):
    documentos = data.get('Documentos', {}).get('Opcoes', [])
    parsed_data = {}

    multiplicador = documentos.get('Multiplicador', [])

    for item in multiplicador:
        grupo = item.get('grupo')
        if grupo:
            parsed_data[grupo] = {
                'max': item.get('max', 1),
                'buscador': item.get('buscador', '')
            }
    return parsed_data

def options_yaml_options(data):
    """
    Collect general options from the YAML data.
    
    :param data: Dictionary containing the parsed YAML data.
    :return: Dictionary with parsed options.
    """
    documentos = data.get('Documentos', {}).get('Opcoes', {})
    parsed_data = {
        'multiplicador': [],
        'regras': documentos.get('Regras', []),
        'db': documentos.get('DB', False),
        'db_table': []
    }

    # Processar o Multiplicador
    multiplicador = documentos.get('Multiplicador', [])
    if isinstance(multiplicador, list):
        parsed_data['multiplicador'] = multiplicador
    elif isinstance(multiplicador, dict):
        parsed_data['multiplicador'] = [multiplicador]

    # Processar DB-table
    for table in documentos.get('DB-table', []):
        table_data = {
            'nome': table.get('nome', ''),
            'form-factory': table.get('form-factory', False),
            'uid': table.get('uid', ''),
            'campos': {},
            'regra': []
        }
        
        for campo in table.get('campos', []):
            if isinstance(campo, dict):
                for key, value in campo.items():
                    table_data['campos'][key] = value
            elif isinstance(campo, str):
                table_data['campos'][campo] = ""

        # Processar regras
        for regra in table.get('regra', []):
            if isinstance(regra, dict):
                table_data['regra'].append(regra)

        parsed_data['db_table'].append(table_data)

    return parsed_data