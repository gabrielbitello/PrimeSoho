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
                'grupo': item.get('grupo', '')
            }
    return parsed_data

def parse_yaml_options(data):
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
