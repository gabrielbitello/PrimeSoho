import os
import uuid
from docx import Document
from num2words import num2words  # Para converter números em texto

def adicionar_ou_criar_tabela(doc, paragrafo, campo, valor):
    """
    Se o campo estiver em uma tabela, adiciona uma linha abaixo.
    Se o campo NÃO estiver em uma tabela, cria uma nova tabela e adiciona o campo nela.
    """
    encontrou_tabela = False

    # Verificando se já existe uma tabela com o campo
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    if f"{{{campo}}}" in p.text:
                        encontrou_tabela = True
                        nova_linha = table.add_row()
                        # Garantir que a nova linha tenha pelo menos 2 células
                        if len(nova_linha.cells) < 2:
                            nova_linha.add_cell()  # Usando o método add_cell para adicionar uma célula
                            nova_linha.add_cell()  # Outra célula

                        nova_linha.cells[0].text = campo
                        nova_linha.cells[1].text = str(valor) if valor else ""
                        return

    # Se o campo não estava em nenhuma tabela, cria uma nova tabela abaixo do parágrafo
    if not encontrou_tabela:
        nova_tabela = doc.add_table(rows=1, cols=2)
        nova_tabela.style = 'Table Grid'  # Ajusta o estilo da tabela
        nova_tabela.rows[0].cells[0].text = campo
        nova_tabela.rows[0].cells[1].text = str(valor) if valor else ""

        # Inserir a tabela logo abaixo do parágrafo
        paragrafo.insert_paragraph_before("")._element.addnext(nova_tabela._element)

def converter_numero_para_texto(valor):
    """Converte um número para texto em português."""
    if valor is None:
        return ""
    try:
        return num2words(int(valor), lang='pt_BR')
    except ValueError:
        return ""

def substituir_texto(paragrafo, campo, valor):
    """Substitui todas as ocorrências de {campo} no parágrafo por valor."""
    if f"{{{campo}}}" in paragrafo.text:
        novo_texto = paragrafo.text.replace(f"{{{campo}}}", str(valor) if valor else "")
        paragrafo.clear()
        paragrafo.add_run(novo_texto)

def gen_docx(dados, folder, yaml_data):
    """Preenche o modelo DOCX com os dados do formulário e do YAML."""
    caminho_template = os.path.abspath(os.path.join('app', 'docs', folder, f'{folder}.docx'))
    doc = Document(caminho_template)
    unique_id = str(uuid.uuid4())[:8]

    # Adicionando variáveis do YAML aos dados
    for campo_yaml in yaml_data.get('Documentos', {}).get('Documentos-Config', []):
        nome_campo = campo_yaml.get('nome')
        if nome_campo:
            variaveis = campo_yaml.get('variaveis', [None])
            if nome_campo not in dados:
                dados[nome_campo] = variaveis[0] if variaveis else None

    # Substituição de variáveis no documento e aplicação das regras
    for p in doc.paragraphs:
        for campo, valor in dados.items():
            campo_yaml = next((c for c in yaml_data.get('Documentos', {}).get('Documentos-Config', []) if c.get('nome') == campo), None)

            if campo_yaml:  # Verifica se a variável existe
                regras = campo_yaml.get('regras', {})  # Garante que regras seja um dicionário

                # Aplicando as regras se existirem
                if regras and regras.get('Number_To_Text', False):
                    valor = converter_numero_para_texto(valor)

                # Verifica e aplica a regra de adicionar uma tabela se necessário
                if regras and regras.get('Add_box', False):
                    adicionar_ou_criar_tabela(doc, p, campo, valor)

                # Substituição do campo pelo valor
                substituir_texto(p, campo, valor)

    # Verificando tabelas no documento e substituindo tags dentro delas
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for campo, valor in dados.items():
                        campo_yaml = next((c for c in yaml_data.get('Documentos', {}).get('Documentos-Config', []) if c.get('nome') == campo), None)

                        if campo_yaml:  # Verifica se a variável existe
                            regras = campo_yaml.get('regras', {})  # Garante que regras seja um dicionário

                            # Aplicando as regras de número e tabela se necessário
                            if regras and regras.get('Number_To_Text', False):
                                valor = converter_numero_para_texto(valor)

                            if regras and regras.get('Add_box', False):
                                adicionar_ou_criar_tabela(doc, p, campo, valor)

                        # Substituição do campo pelo valor
                        substituir_texto(p, campo, valor)

    # Salvar o arquivo gerado
    caminho_saida = os.path.abspath(f'./app/output/{folder}_preenchido_{unique_id}.docx')
    doc.save(caminho_saida)

    return caminho_saida
