from django.contrib import admin
from .models import Imoveis, Visita, Proposta

@admin.register(Imoveis)
class ImoveisAdmin(admin.ModelAdmin):
    list_display = ('endereco', 'numero', 'bairro', 'cidade', 'valor', 'tipo', 'destaque', 'matricula')
    list_filter = ('cidade', 'tipo', 'destaque', 'divulgar')
    search_fields = ('endereco', 'bairro', 'cidade', 'ref')
    filter_horizontal = ('proprietario',)
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('endereco', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'cep', 'tipo', 'ref')
        }),
        ('Detalhes do Imóvel', {
            'fields': ('descricao', 'valor', 'area_total', 'area_privativa', 'quartos', 'banheiros', 'garagem', 'suites', 'lavabos', 'salas')
        }),
        ('Características', {
            'fields': ('area_servico', 'sacada', 'churrasqueira', 'piscina', 'academia', 'salao_festas', 'playground', 'quadra', 'lavanderia', 'mobiliado')
        }),
        ('Informações Adicionais', {
            'fields': ('imagems', 'angariador', 'indicador', 'porcentagem', 'proprietario', 'divulgar', 'destaque')
        }),
        ('Documentação e Pagamento', {
            'fields': ('condicoes_pagamento', 'documentos', 'matricula', 'indicacao_fiscal', 'valor_condominio', 'iptu')
        }),
        ('Detalhes do Edifício', {
            'fields': ('andar', 'elevador', 'portaria')
        }),
        ('Exclusividade', {
            'fields': ('exclusividade', 'tempo_exclusividade')
        }),
        ('Acesso', {
            'fields': ('chave',)
        }),
    )

@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'imovel', 'data_visita', 'confirmacao')
    list_filter = ('confirmacao', 'data_visita')
    search_fields = ('cliente__nome', 'imovel__endereco')
    date_hierarchy = 'data_visita'

@admin.register(Proposta)
class PropostaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'imovel', 'data_proposta', 'valor_proposta')
    list_filter = ('data_proposta',)
    search_fields = ('cliente__nome', 'imovel__endereco')
    date_hierarchy = 'data_proposta'
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('cliente', 'imovel', 'data_proposta', 'valor_proposta')
        }),
        ('Detalhes Financeiros', {
            'fields': ('entrada', 'tipo_entrada', 'financiamento', 'fgts', 'sinal', 'tipo_sinal')
        }),
        ('Troca', {
            'fields': ('imovel_troca', 'veiculo_troca')
        }),
        ('Condições e Observações', {
            'fields': ('condicao_entrega', 'ficam_no_imovel', 'observacao')
        }),
    )