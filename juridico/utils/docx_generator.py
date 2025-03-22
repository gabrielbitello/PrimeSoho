import os
import uuid
from num2words import num2words
from docx import Document
import re
from copy import deepcopy
import datetime

counter_dict = {}
subcounter_dict = {}


# Obtém o diretório do app 'juridico'
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define o caminho para o diretório 'docs' no mesmo diretório que o arquivo views.py
docs_path = os.path.join(parent_dir, 'docs')

output_path = os.path.join(parent_dir, 'output')



def criar_tabela_ao_redor_do_valor(paragrafo, valor):
    """Cria uma tabela simples ao redor do valor, adicionando o valor à célula da tabela."""
    # Cria uma tabela com uma linha e uma coluna (ao redor do valor)
    tabela = paragrafo.add_paragraph().add_run().add_table(rows=1, cols=1)

    # Adiciona o valor à célula da tabela
    celula = tabela.cell(0, 0)
    celula.text = valor

    # Aplica estilo à tabela (bordas internas apenas)
    tabela.style = 'Table Grid'

    # Retorna o parágrafo com a tabela ao redor do valor
    return paragrafo

def converter_numero_para_texto(valor):
    if valor is None:
        return ""
    try:
        valor_str = str(valor).replace('.', '').replace(' ', '')
        return num2words(int(valor_str), lang='pt_BR')
    except ValueError:
        return ""

def substituir_texto(paragrafo, campo, valor):
    """Substitui todas as ocorrências de {campo} no parágrafo por valor."""
    campo_formatado = f"{{{campo}}}"
    if campo_formatado in paragrafo.text:
        novo_texto = paragrafo.text.replace(campo_formatado, str(valor) if valor else "")
        paragrafo.clear()
        paragrafo.add_run(novo_texto)

def parse_string(input_str):
    if ":" in input_str:
        parts = input_str.split(":")
        x = parts[0]
        if "/" in parts[1]:
            y, modifier = parts[1].split("/")
        else:
            y = parts[1]
            modifier = None
        return x, y, modifier
    
    elif "/" in input_str:
        x, modifier = input_str.split("/")
        return x, None, modifier
    
    else:
        return input_str, None, None


def aplicar_regras_para_valor(valor, yaml_data, campo_verificado, doc, dados, yaml):
    """Aplica as regras de forma automática com base nas configurações no YAML para o valor da variável."""

    # Se não houver regras, retornamos o valor sem alteração
    if not yaml_data.get('regras'):
        return valor

    # Obtém as regras para o campo verificado, se houver
    regras_aplicadas = yaml_data.get('regras', [])

    # Iterando sobre as regras (agora assumimos que é uma lista)
    for regra_obj in regras_aplicadas:
        if isinstance(regra_obj, dict):
            for regra, regra_valor in regra_obj.items():
                
                # Exemplo de regra para adicionar uma caixa
                if regra == "Add_box" and regra_valor:
                    inc = "inc"  # Placeholder para ação necessária
                
                # Converte número para texto, se a regra for válida
                elif regra == "Number_To_Text" and isinstance(regra_valor, str):
                    valor_para_converter = dados.get(regra_valor, None)
                    if valor_para_converter is not None:
                        valor = converter_numero_para_texto(valor_para_converter)
                
                # Aplica formatação de texto substituindo chaves por valores correspondentes
                elif regra == "Formater" and isinstance(regra_valor, str):
                    def substituir_variavel(match):
                        chave = match.group(1)

                        # Tenta buscar no dicionário `dados`
                        if chave in dados and dados[chave] is not None:
                            return str(dados[chave])
                        else:
                            # Busca no YAML dentro de `Documentos-Config`
                            documentos_config = yaml.get('Documentos', {}).get('Documentos-Config', [])
                            item_filtrado = next((item for item in documentos_config if item.get('nome') == chave), None)

                            if item_filtrado:

                                if item_filtrado.get('regras') or item_filtrado.get('condicao'):

                                    if not verificar_condicoes(dados, item_filtrado, None):
                                        return ""

                                    variaveis_yaml = item_filtrado.get('variaveis', [])
                                    novo_valor = variaveis_yaml[0] if variaveis_yaml else None

                                    # Se `novo_valor` for None, aplicar regras adicionais
                                    if novo_valor is None:
                                        novo_valor = aplicar_regras_para_valor(None, item_filtrado, chave, doc, dados, None)
                                    
                                    return str(novo_valor) if novo_valor is not None else match.group(0)

                            return ""

                    valor = re.sub(r'\{(.*?)\}', substituir_variavel, regra_valor)
                
                # Aplica contagem a partir de um valor usando regex
                elif regra == "Counter" and isinstance(regra_valor, str):
                    XY_value = regra_valor
                    if XY_value:
                        x, y, modifier = parse_string(XY_value)
                        counter_value = get_counter_value(x, y)
                        if modifier == "B":
                            counter_value = f"**{counter_value} - **"  # Adiciona marcadores de negrito
                        
                        valor = counter_value + valor # Mantém o fluxo de valor corretamente

    return valor

def get_counter_value(x, y=None):
    x = int(x) 
    y = int(y) if y is not None else None  
    # Se X ainda não foi inicializado, ele começa em 1 (sem incrementar ainda)
    if x not in counter_dict:
        counter_dict[x] = 1
        subcounter_dict[x] = {}

    # Se Y está presente, não incrementa X, mas usa o valor atual dele e gerencia Y
    if y is not None:
        if y not in subcounter_dict[x]:
            subcounter_dict[x][y] = 1  
        else:
            subcounter_dict[x][y] += 1 
        return f"{counter_dict[x] - 1}.{subcounter_dict[x][y]}"  
    
    # Se Y for 'Y' e X for 0, altere X para 1 automaticamente
    if y == 'Y' and x == '0':
        x  = '1'
        

    # Se Y não está presente, apenas incrementa X e retorna o valor atualizado
    valor_atual = counter_dict[x]  
    counter_dict[x] += 1  

    return str(valor_atual)

# Função auxiliar para substituição dinâmica
def substituir_match(match):
    x = match.group(1)
    y = match.group(2)
    
    novo_valor = get_counter_value(x, y) if y else get_counter_value(x)
    return str(novo_valor)

def processar_dados(dados, parsed_data_options):
    novos_dados = {}
    contadores = {}
    
    print("Processando dados")
    for nome, config in parsed_data_options.items():

        if nome in dados:
            valor = dados[nome]
            if isinstance(valor, list):
                for i, item in enumerate(valor):
                    if isinstance(item, dict):
                        for chave, val in item.items():
                            if chave not in contadores:
                                contadores[chave] = 0
                            else:
                                contadores[chave] += 1
                            nova_chave = f"form-{contadores[chave]}-{chave}"
                            novos_dados[nova_chave] = val
                    else:
                        nova_chave = f"form-{i}-{nome}"
                        novos_dados[nova_chave] = item
            elif isinstance(valor, dict):
                for chave, val in valor.items():
                    if chave not in contadores:
                        contadores[chave] = 0
                    else:
                        contadores[chave] += 1
                    nova_chave = f"form-{contadores[chave]}-{chave}"
                    novos_dados[nova_chave] = val
            else:
                nova_chave = f"form-0-{nome}"
                novos_dados[nova_chave] = valor
    
    return novos_dados

def processar_inputs_especiais(texto_original):
    contadores = {}
    
    def substituir_input(match):
        nome = match.group(1)
        if nome.startswith('form-'):
            # Se já estiver no formato {form-X-Nome}, não alterar
            return match.group(0)
        if nome not in contadores:
            contadores[nome] = 0
        else:
            contadores[nome] += 1
        return f"{{form-{contadores[nome]}-{nome}}}"
    
    # Padrão atualizado para capturar tanto {#Nome} quanto {form-X-Nome}
    padrao = r'{(?:#|\w+-)(\w+)}'
    texto_processado = re.sub(padrao, substituir_input, texto_original)
    
    print(f"Texto original: {texto_original}")
    print(f"Texto processado: {texto_processado}")
    
    return texto_processado

def extrair_nome(chave: str) -> str:
    partes = chave.split('-')
    return '-'.join(partes[2:])  # Ignora as duas primeiras partes


def substituir_variaveis_no_paragrafo(paragrafo, dados, yaml_data, doc, parsed_data_options, linha=None, tabela_o=None):
    """Substitui variáveis no parágrafo conforme as regras, garantindo que cada contador seja atualizado corretamente."""

    # Extrair todo o texto do parágrafo para uma única string
    texto_original = "".join(run.text for run in paragrafo.runs)
    print(f"Texto original: {texto_original}")

    # Processar inputs especiais
    print (f"substituindo texto original")
    texto_processado = processar_inputs_especiais(texto_original)
    print ("texto processado")


    # Limpa os runs atuais do parágrafo
    for run in paragrafo.runs:
        run.text = ""

    # Adiciona o texto processado ao parágrafo
    paragrafo.add_run(texto_processado)

    # Limpa os runs atuais do parágrafo
    for run in paragrafo.runs:
        run.text = ""  # Limpa o texto original do run

    # Adiciona o texto atualizado ao parágrafo
    paragrafo.runs[0].text = texto_processado

    # Expressão regular para encontrar padrões como {counter:x} ou {counter:x:y}
    pattern = r"\{counter:(\d+)(?::(\d+))?\}"

    # Substituir diretamente nos 'runs' do parágrafo
    for run in paragrafo.runs:
        if "{counter:" in run.text:
            run.text = re.sub(pattern, substituir_match, run.text)

    #----------------------------------------------------
    #
    #Problema para substituir variaveis do form-factory se existir mais de 1 campo
    #
    #----------------------------------------------------

    # Processa outras variáveis além de counter
    for chave, valor in dados.items():
        chave_formatada = f"{{{chave}}}"
        if chave.startswith("form"):
            chave_reformatada = extrair_nome(chave)
        else:
            chave_reformatada = chave
        if chave_formatada in texto_processado:
            print(f"Chave especial encontrada: {chave_formatada}")

            documentos_config = yaml_data.get('Documentos', {}).get('Documentos-Config', [])
            item_filtrado = next((item for item in documentos_config if item.get('nome') == chave_reformatada), None)

            if not verificar_condicoes(dados, item_filtrado, chave_reformatada):
                for run in paragrafo.runs:
                    if chave_formatada in run.text:
                        run.text = run.text.replace(chave_formatada, '')
                continue

            novo_valor = valor or ''
            if not novo_valor:
                variaveis_yaml = item_filtrado.get('variaveis', []) if item_filtrado else []
                if variaveis_yaml:
                    novo_valor = variaveis_yaml[0]

            novo_valor = aplicar_regras_para_valor(novo_valor, item_filtrado, chave_reformatada, doc, dados, yaml_data)

            for run in paragrafo.runs:
                if chave_formatada in run.text:
                    novo_texto = run.text.replace(chave_formatada, str(novo_valor))
            
                    # Verifica se o novo valor tem marcadores de negrito (**)
                    if "**" in novo_texto:
                        partes = novo_texto.split("**")
                        run.text = ""  # Limpa o run original para evitar duplicações
            
                        for i, parte in enumerate(partes):
                            if parte:  # Garante que não adicionamos runs vazios
                                novo_run = paragrafo.add_run(parte)
                                if i % 2 == 1:  # Índices ímpares são o texto entre "**"
                                    novo_run.bold = True
                    else:
                        run.text = novo_texto  # Apenas substitui normalmente se não tiver "**"
                
                    # Verifica se tabela_o não é None e o novo texto é vazio
                    if tabela_o is not None and not novo_texto.strip():
                        # Itera sobre as linhas da tabela
                        for linha in tabela_o.rows:
                            # Verifica se todas as células da linha estão vazias
                            if all(not celula.text.strip() for celula in linha.cells):
                                tabela_o._tbl.remove(linha._tr)  # Remove a linha da tabela
                                break  # Sai do loop após remover a linha
        else:
            print(f"Chave não encontrada no texto: {chave_formatada}")
    
    # Reconhecimento de contadores dentro de tabelas
    for tabela in doc.tables:
        for row in tabela.rows:
            for cell in row.cells:
                for paragrafo in cell.paragraphs:
                    for run in paragrafo.runs:
                        if "{counter:" in run.text:
                            run.text = re.sub(pattern, substituir_match, run.text)

    return paragrafo


def substituir_variaveis_nas_tabelas(doc, dados, yaml_data, parsed_data_options):
    """Substitui variáveis dentro de tabelas do documento."""
    for table_index, table in enumerate(doc.tables):
        for row_index, row in enumerate(table.rows):
            for cell_index, cell in enumerate(row.cells):
                for paragrafo in cell.paragraphs:
                    substituir_variaveis_no_paragrafo(paragrafo, dados, yaml_data, doc, parsed_data_options, row, table)

def substituir_variaveis_no_rodape(doc, dados, yaml_data, parsed_data_options):
    """Substitui variáveis nos rodapés do documento."""
    for section in doc.sections:
        for rodape in section.footer.paragraphs:
            substituir_variaveis_no_paragrafo(rodape, dados, yaml_data, doc, parsed_data_options)

def substituir_variaveis_no_cabecalho(doc, dados, yaml_data, parsed_data_options):
    """Substitui variáveis nos cabeçalhos do documento."""
    for section in doc.sections:
        for cabecalho in section.header.paragraphs:
            substituir_variaveis_no_paragrafo(cabecalho, dados, yaml_data, doc, parsed_data_options)

def verificar_condicoes(dados, yaml_data, campo_verificado):
    """Verifica as condições de um campo, buscando no YAML as condições associadas ao campo."""

    # Obtém as condições do YAML relacionadas ao campo
    condicao = yaml_data.get('condicao', {})

    if not condicao:
        return True  # Se não houver condição, o campo é considerado válido.

    if not isinstance(condicao, dict):
        return False

    # Itera sobre as condições para o campo
    for chave, valor in condicao.items():

        # Caso a chave contenha o caractere '/', ela deve ser dividida e tratada como um "OU"
        if '/' in chave:
            # Dividir a chave pelo '/' e verificar se ao menos uma das partes tem o valor esperado
            chaves = chave.split('/')
            condicao_atendida = False

            for chave_parte in chaves:
                if chave_parte in dados:
                    campo_valor = dados[chave_parte]

                    # Verifica se o valor da condição é uma lista
                    if isinstance(valor, list):
                        if campo_valor in valor:
                            condicao_atendida = True
                            break
                    # Verifica a condição booleana
                    elif isinstance(valor, bool):
                        if valor and not campo_valor:
                            return False
                        elif not valor and campo_valor:
                            return False
                    # Caso a condição seja um valor simples
                    elif campo_valor == valor:
                        condicao_atendida = True
                        break

            if not condicao_atendida:
                return False

        else:
            if chave in dados:
                campo_valor = dados[chave]

                # Verifica se o valor da condição é uma lista
                if isinstance(valor, list):
                    if campo_valor not in valor:
                        return False
                # Verifica a condição booleana
                elif isinstance(valor, bool):
                    if valor and not campo_valor:
                        return False
                    elif not valor and campo_valor:
                        return False
                # Caso a condição seja um valor simples
                elif campo_valor != valor:
                    return False
            else:
                return False

    return True  # Se todas as condições foram atendidas

def inserir_tabela_apos(tabela_original, nova_tabela):
    """Insere uma tabela duplicada após a tabela original."""
    tabela_elemento_original = tabela_original._element
    nova_tabela_elemento = nova_tabela._element
    tabela_elemento_original.addnext(nova_tabela_elemento)

def inserir_linha_abaixo(tabela, linha_original):
    """Insere uma nova linha logo abaixo da linha original da tabela."""
    # Cria uma nova linha com células vazias, com o mesmo número de células da linha original
    nova_linha = tabela.add_row()

    for i, celula in enumerate(linha_original.cells):
        nova_linha.cells[i].text = ""  # Você pode definir o conteúdo da nova linha aqui, se necessário


def gen_docx(dados, folder, yaml_data, parsed_data_options):
    """Preenche o modelo DOCX com os dados do formulário e do YAML."""
    caminho_template = os.path.abspath(os.path.join(docs_path, folder, f'{folder}.docx'))

    unique_id = str(uuid.uuid4())[:8]

    # Adiciona variáveis do YAML aos dados, se ainda não existirem
    for campo_yaml in yaml_data.get('Documentos', {}).get('Documentos-Config', []):
        nome_campo = campo_yaml.get('nome')
        if nome_campo and nome_campo not in dados:
            if not campo_yaml.get('grupo'):
                dados[nome_campo] = None

    # Carrega o arquivo DOCX
    doc = Document(caminho_template)

    for grupo in parsed_data_options:
        if grupo in dados:
            print (f"Grupo: {grupo}")
            buscador = parsed_data_options[grupo].get('buscador')
            print (f"Buscador: {buscador}")
            multiplicador = dados[grupo]
            numero_de_dicionarios = sum(1 for item in multiplicador if isinstance(item, dict))
            numero_de_dicionarios = numero_de_dicionarios - 1

            if numero_de_dicionarios:
                for tabela in doc.tables:
                    for linha in tabela.rows:
                        for celula in linha.cells:
                            if buscador in celula.text:
                                # Encontrou a tabela que contém o texto do buscador
                                tabela_original = tabela
                                for _ in range(numero_de_dicionarios):
                                    # Cria uma cópia da tabela original
                                    nova_tabela = deepcopy(tabela_original)

                                    # Insere a nova tabela logo após a tabela original
                                    inserir_tabela_apos(tabela_original, nova_tabela)
                                    print (f"Nova tabela inserida após a tabela original.")
                                break

    print ("processando dados")
    dados_processados = processar_dados(dados, parsed_data_options)
    for chave, valor in dados_processados.items():
        dados[chave] = valor
    for grupo in parsed_data_options:
        del dados[grupo]
    print (f"dados processados: {dados_processados} e dados: {dados}")	

    if not doc.paragraphs:
        raise ValueError(f"O template {caminho_template} não contém parágrafos.")

    # Substituição de variáveis no documento
    for paragrafo in doc.paragraphs:
        substituir_variaveis_no_paragrafo(paragrafo, dados, yaml_data, doc, parsed_data_options)

    # Substituição dentro das tabelas
    substituir_variaveis_nas_tabelas(doc, dados, yaml_data, parsed_data_options)

    # Substituição no rodapé
    substituir_variaveis_no_rodape(doc, dados, yaml_data, parsed_data_options)

    # Substituição no cabeçalho
    substituir_variaveis_no_cabecalho(doc, dados, yaml_data, parsed_data_options)

    # Salva o arquivo gerado
    caminho_saida = f'{folder}_preenchido_{unique_id}.docx'
    output_path_formated = os.path.abspath(os.path.join(output_path, caminho_saida))
    doc.save(output_path_formated)

    return caminho_saida