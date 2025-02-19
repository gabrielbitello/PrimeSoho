import os
import uuid
from num2words import num2words
from docx import Document
import re

counter_dict = {}
subcounter_dict = {}

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
    """Converte um número para texto em português."""
    if valor is None:
        return ""
    try:
        return num2words(int(valor), lang='pt_BR')
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
    if ':' in input_str:
        x, y = input_str.split(':')
        return x, y
    else:
        x = input_str
        y = None
        return x, y

def aplicar_regras_para_valor(valor, yaml_data, campo_verificado, doc, dados):
    """Aplica as regras de forma automática com base nas configurações no YAML para o valor da variável."""
    
    # Se não houver regras, retornamos o valor sem alteração
    if not yaml_data.get('regras'):
        print("Nenhuma regra encontrada para aplicar.")
        return valor

    # Obtém as regras para o campo verificado, se houver
    regras_aplicadas = yaml_data.get('regras', [])
    print(f"\nAplicando regras para o campo '{campo_verificado}': {regras_aplicadas}")

    # Iterando sobre as regras (agora assumimos que é uma lista)
    for regra_obj in regras_aplicadas:
        print(f"Processando a regra: {regra_obj}")  # Adicionando debug para verificar cada regra

        if isinstance(regra_obj, dict):
            for regra, regra_valor in regra_obj.items():
                print(f" - Regra: {regra}, Valor da regra: {regra_valor}")  # Debug detalhado da regra

                # Exemplo de regra para adicionar uma caixa (não implementado, mas podemos colocar o valor dentro de uma tabela ou similar)
                if regra == "Add_box" and regra_valor:
                    print("Aplicando a regra 'Add_box'.")
                    # Aqui você pode adicionar a lógica para adicionar o valor à tabela ou o que for necessário
                    print("erro esotu disparando a mesma regra varias x")
                    inc = "inc"  # Exemplo, mas pode ser qualquer ação necessária

                # Converte número para texto, se a regra for válida
                elif regra == "Number_To_Text" and isinstance(regra_valor, str):
                    valor_para_converter = dados.get(regra_valor, None)
                    if valor_para_converter is not None:
                        valor = converter_numero_para_texto(valor_para_converter)
                        print(f" - Convertendo número para texto: {valor_para_converter} -> {valor}")
                    else:
                        print(f" - Valor não encontrado para converter: {regra_valor}")

                # Aplica contagem a partir de um valor usando regex (exemplo de contador)
                elif regra == "Counter" and isinstance(regra_valor, str):
                    XY_value = regra_valor
                    if XY_value:
                        x, y = parse_string(XY_value)
                        counter_value = get_counter_value(x, y)
                        valor = counter_value + valor  # Ajustado para somar o contador ao valor
                        print(f" - Aplicando contador: {counter_value} + {valor}")
                    else:
                        print(f" - Formato inválido para contador: {regra_valor}")

                # Adicione outras regras conforme necessário
                # ...
    return valor

def get_counter_value(x, y=None):
    if x not in counter_dict:
        counter_dict[x] = 1
        subcounter_dict[x] = {}
    else:
        if y is None:
            counter_dict[x] += 1
    
    if y is not None:
        if y not in subcounter_dict[x]:
            subcounter_dict[x][y] = 1
        else:
            subcounter_dict[x][y] += 1
        return f"{x}.{subcounter_dict[x][y]}"
    else:
        return str(counter_dict[x])
    
def substituir_variaveis_no_paragrafo(paragrafo, dados, yaml_data, doc):
    """Substitui variáveis no parágrafo conforme as regras e condições, mantendo a formatação e sem modificar o dicionário 'dados'."""

    # Obtém o texto original do parágrafo
    texto_original = paragrafo.text
    print(f"Texto original do parágrafo: {texto_original}")  # Debug

    # Processa linha por linha e variável por variável
    for chave, valor in dados.items():
        chave_formatada = f"{{{chave}}}"  # Variáveis são referenciadas como {variavel}

        if chave_formatada in texto_original:
            print(f"Encontrou a chave: {chave_formatada}")  # Debug

            # Verifica se o formato da chave é "counter:x:y" ou "counter:x"
            if chave.startswith("counter:"):
                # Usar expressão regular para capturar o padrão "counter:x" ou "counter:x:y"
                pattern = r"\{counter:(\d+)(?::(\d+))?\}"  # Expressão para capturar números após counter
                matches = re.findall(pattern, texto_original)

                # Para cada correspondência, substituir com o valor correto
                for match in matches:
                    x = match[0]  # A primeira parte (x)
                    y = match[1] if match[1] else None  # Se houver uma segunda parte (y), usar, senão None
                    
                    print(f"Encontrou contador: x={x}, y={y}")  # Debug

                    # Chama a função get_counter_value de acordo com os valores de x e y
                    if y:
                        novo_valor = get_counter_value(x, y)
                    else:
                        novo_valor = get_counter_value(x)
                    
                    # Substitui no texto original o contador encontrado pelo novo valor
                    texto_original = texto_original.replace(f"{{counter:{x}{(':' + y) if y else ''}}}", str(novo_valor))
                    print(f"Substituído {chave_formatada} por {novo_valor}")  # Debug

            else:
                # Obtém a configuração específica do YAML
                documentos_config = yaml_data.get('Documentos', {}).get('Documentos-Config', [])
                item_filtrado = next((item for item in documentos_config if item.get('nome') == chave), None)

                # Verifica se há condições para essa variável e se elas são atendidas
                if not verificar_condicoes(dados, item_filtrado, chave):
                    continue  # Se a condição falhar, não substitui a variável

                # Verifica se o valor da variável ainda está vazio
                novo_valor = valor or ''
                if not novo_valor:
                    # Caso o valor esteja vazio, atribuir o primeiro valor do campo "variáveis" no YAML
                    variaveis_yaml = item_filtrado.get('variaveis', {})
                    if variaveis_yaml:
                        novo_valor = variaveis_yaml[0]  # Atribui o primeiro valor de 'variaveis'
                    print(f"Novo valor após verificação de variável YAML: {novo_valor}")  # Debug

                # Aplica regras antes de retornar o valor
                novo_valor = aplicar_regras_para_valor(novo_valor, item_filtrado, chave, doc, dados)
                print(f"Novo valor após aplicação de regras: {novo_valor}")  # Debug

            # Mantém a formatação e substitui apenas a variável nos 'runs'
            for run in paragrafo.runs:
                if chave_formatada in run.text:
                    print(f"Substituindo '{chave_formatada}' por '{novo_valor}' no run.")  # Debug
                    run.text = run.text.replace(chave_formatada, str(novo_valor))

    return paragrafo




def substituir_variaveis_nas_tabelas(doc, dados, yaml_data):
    """Substitui variáveis dentro de tabelas do documento."""
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragrafo in cell.paragraphs: 
                    substituir_variaveis_no_paragrafo(paragrafo, dados, yaml_data, doc)

def verificar_condicoes(dados, yaml_data, campo_verificado):
    """Verifica as condições de um campo, buscando no YAML as condições associadas ao campo."""

    # Obtém as condições do YAML relacionadas ao campo
    condicao = yaml_data.get('condicao', {})

    if not condicao:
        print(f"Sem condição definida para o campo '{campo_verificado}', campo considerado válido.")
        return True  # Se não houver condição, o campo é considerado válido.

    if not isinstance(condicao, dict):
        print(f"Condição para '{campo_verificado}' não é um dicionário. Retornando False.")
        return False

    # Itera sobre as condições para o campo
    for chave, valor in condicao.items():
        print(f"\nVerificando condição para a chave '{chave}' no campo '{campo_verificado}':")
        
        if chave in dados:
            campo_valor = dados[chave]
            print(f" - A chave '{chave}' foi encontrada nos dados com o valor '{campo_valor}'.")

            # Verifica a condição booleana
            if isinstance(valor, bool):
                if valor:  # Espera que o campo tenha um valor
                    if not campo_valor:
                        print(f"   - A condição booleana falhou: Esperava valor em '{chave}', mas o valor é vazio ou None.")
                        return False
                    else:
                        print(f"   - A condição booleana foi atendida: '{chave}' tem um valor.")
                else:  # Espera que o campo NÃO tenha valor
                    if campo_valor:
                        print(f"   - A condição booleana falhou: Esperava campo vazio em '{chave}', mas o valor encontrado é '{campo_valor}'.")
                        return False
                    else:
                        print(f"   - A condição booleana foi atendida: '{chave}' está vazio ou None.")
            
            elif campo_valor != valor:  # Verifica se o valor do campo é o esperado
                print(f"   - A condição falhou: '{campo_valor}' != {valor}")
                return False
            else:
                print(f"   - A condição foi atendida: '{campo_valor}' == {valor}")
        else:
            print(f"   - A chave '{chave}' não foi encontrada nos dados. Condição não atendida.")
            return False

    return True  # Se todas as condições foram atendidas

def gen_docx(dados, folder, yaml_data):
    """Preenche o modelo DOCX com os dados do formulário e do YAML."""
    caminho_template = os.path.abspath(os.path.join('app', 'docs', folder, f'{folder}.docx'))
    print(f"Carregando o template: {caminho_template}")

    unique_id = str(uuid.uuid4())[:8]

    # Adiciona variáveis do YAML aos dados, se ainda não existirem
    for campo_yaml in yaml_data.get('Documentos', {}).get('Documentos-Config', []):
        nome_campo = campo_yaml.get('nome')
        if nome_campo and nome_campo not in dados:
            dados[nome_campo] = campo_yaml.get('variaveis', [None])[0] or ""

    # Carrega o arquivo DOCX
    doc = Document(caminho_template)

    if not doc.paragraphs:
        raise ValueError(f"O template {caminho_template} não contém parágrafos.")

    # Substituição de variáveis no documento
    for paragrafo in doc.paragraphs:
        substituir_variaveis_no_paragrafo(paragrafo, dados, yaml_data, doc)

    # Substituição dentro das tabelas
    substituir_variaveis_nas_tabelas(doc, dados, yaml_data)

    # Salva o arquivo gerado
    caminho_saida = os.path.abspath(f'./app/output/{folder}_preenchido_{unique_id}.docx')
    doc.save(caminho_saida)
    return caminho_saida
