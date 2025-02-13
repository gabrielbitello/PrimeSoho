import os
from docx import Document

# Função para gerar o documento DOCX
def gen_docx(dados, folder, yaml_data):
    """Preenche o modelo DOCX com os dados do formulário e do YAML"""
    caminho_template = os.path.abspath(os.path.join('app', 'docs', folder, f'{folder}.docx'))
    doc = Document(caminho_template)

    print(f"Template carregado: {caminho_template}")
    print(f"Dados recebidos: {dados}")
    print(f"YAML carregado: {yaml_data}")

    # Adicionando variáveis do YAML aos dados
    for campo_yaml in yaml_data.get('Documentos', {}).get('Documentos-Config', []):
        nome_campo = campo_yaml.get('nome')
        if nome_campo:
            print(f"\nAnalisando campo YAML: {nome_campo}")
        
        # Garantir que todos os campos do YAML estão no dicionário `dados`
        if nome_campo and nome_campo not in dados:
            valor_default = campo_yaml.get('variaveis', [None])[0]
            print(f"Campo {nome_campo} não encontrado nos dados. Atribuindo valor default: {valor_default}")
            dados[nome_campo] = valor_default

    # Verificação de condições
    for campo_yaml in yaml_data.get('Documentos', {}).get('Documentos-Config', []):
        nome_campo = campo_yaml.get('nome')
        condicoes = campo_yaml.get('condicao', {})
        form_false = campo_yaml.get('form', False)
        
        print(f"\nVerificando campo: {nome_campo} com 'form: {form_false}'")

        if form_false is False:
            condicao_atendida = True
            if isinstance(condicoes, dict):  # Garante que condicoes é um dicionário
                for condicao_campo, condicao_valor in condicoes.items():
                    if condicao_campo in dados and dados[condicao_campo] != condicao_valor:
                        condicao_atendida = False
                        print(f"Condição falhou para {nome_campo}: {condicao_campo} != {condicao_valor}")
                        break
            
            if condicao_atendida:
                valor_atribuido = campo_yaml.get('variaveis', [None])[0]
                print(f"Condições atendidas. Atribuindo valor: {valor_atribuido}")
                dados[nome_campo] = valor_atribuido
        else:
            if nome_campo not in dados:
                valor_default = campo_yaml.get('variaveis', [None])[0]
                print(f"Form true. Atribuindo valor default: {valor_default}")
                dados[nome_campo] = valor_default

    # Debug específico para Pagamento_Cheque
    if 'Pagamento_Cheque' in dados:
        print(f"\nValor final de 'Pagamento_Cheque': {dados['Pagamento_Cheque']}")
    else:
        print("\n'Pagamento_Cheque' não foi atribuído!")

    # Substituição de variáveis no documento
    for p in doc.paragraphs:
        for campo, valor in dados.items():
            if campo in p.text:
                inline = p.runs
                for item in inline:
                    if campo in item.text:
                        print(f"\nSubstituindo no parágrafo: {campo} -> {valor}")
                        if valor:
                            item.text = item.text.replace(f'{{{campo}}}', str(valor))
                        else:
                            item.text = item.text.replace(f'{{{campo}}}', "")

    # Removendo parágrafos com campos não preenchidos
    for p in doc.paragraphs:
        for campo, valor in dados.items():
            if campo in p.text and not valor:
                print(f"\nRemovendo parágrafo com campo não preenchido: {campo}")
                p.clear()

    # Salvar o arquivo gerado
    caminho_saida = os.path.abspath(f'./app/output/{folder}_preenchido.docx')
    doc.save(caminho_saida)
    print(f"\nDocumento gerado com sucesso em: {caminho_saida}")

    return caminho_saida






# Falta adicionar a regra addbox, a função/regra counter e a regra Number_To_Text e por ultimo ajustar formatação do texto, adiconar unique id a docx