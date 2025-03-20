def opcoes_generator(opcoes):
    
    opcoes_formatadas = ''  # Aqui armazenamos as opções formatadas
    if opcoes:
            campos = '<div class="class-mutiplicador">'
            for nome, campo in opcoes.items():

                max = campo.get('max', 1)
                if max <= 0:
                    max = 1

                campos += '<div class="flex">'
                campos += f'<div>\n<label for="{nome}">Numero de {nome}:</label>\n<input type="number" name="{nome}" id="{nome}" class="form-control multiplicador" value="1" placeholder="1" max={max} min="1"/>\n</div>\n'
                campos += f'<button id="{nome}" class="form-control multiplicador" data-grupo="{nome}" onclick="alert(\'Numero alterado!\')">Confirmar</button>\n'
                campos == '</div>'
            campos += '</div>'
            opcoes_formatadas += campos
    print (opcoes_formatadas)
    return opcoes_formatadas