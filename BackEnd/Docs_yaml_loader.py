import yaml
import os

def load_yaml(filepath):
    """
    Lê e carrega um arquivo YAML.
    Retorna os dados como um dicionário Python.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            return data
    except Exception as e:
        print(f"Erro ao carregar o YAML: {e}")
        return None

def validate_yaml(data):
    """
    Valida se a estrutura do YAML está correta.
    Retorna True se for válido, False caso contrário.
    """
    if not data or 'Documentos' not in data or 'Documentos-Config' not in data['Documentos']:
        print("Erro: Estrutura YAML inválida.")
        return False
    
    for item in data['Documentos']['Documentos-Config']:
        if 'nome' not in item or 'tipo' not in item or 'form' not in item:
            print(f"Erro: Configuração inválida em {item}")
            return False
    
    return True

def parse_yaml(data):
    """
    Transforma os dados do YAML em um formato mais utilizável.
    Retorna uma lista de dicionários com os campos organizados.
    """
    documentos = data['Documentos']['Documentos-Config']
    parsed_data = {}
    
    for item in documentos:
        nome = item.get('nome')
        parsed_data[nome] = {
            'tipo': item.get('tipo'),
            'descricao': item.get('descricao', ''),
            'requerido': item.get('requerido', False),
            'condicao': item.get('condicao', {}),
            'variaveis': item.get('variaveis', []),
            'regras': item.get('regras', {}),
            'grupo': item.get('grupo', '')
        }
    
    return parsed_data

def find_yaml_files(base_path):
    """
    Explora a pasta 'Docs' na raiz do projeto, identifica as subpastas e procura arquivos YAML.
    """
    parent_path = os.path.dirname(base_path)  # Volta uma diretoria
    docs_path = os.path.join(parent_path, 'Docs')
    yaml_files = {}
    
    if not os.path.exists(docs_path):
        print(f"Erro: Pasta 'Docs' não encontrada em {parent_path}")
        return yaml_files
    
    for folder in os.listdir(docs_path):
        folder_path = os.path.join(docs_path, folder)
        if os.path.isdir(folder_path):
            yaml_file = os.path.join(folder_path, f"{folder}.yaml")
            if os.path.exists(yaml_file):
                yaml_files[folder] = yaml_file
    
    return yaml_files

# Testando o carregamento dinâmico
if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    yaml_files = find_yaml_files(base_path)
    
    for folder, yaml_path in yaml_files.items():
        yaml_data = load_yaml(yaml_path)
        
        if yaml_data and validate_yaml(yaml_data):
            parsed = parse_yaml(yaml_data)
            print(f"YAML da pasta '{folder}' carregado e processado com sucesso!")
            print(parsed)