from django.contrib import admin
from .models import Cliente, Uniao, Carteira, OfertaAtiva

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'telefone', 'email', 'cidade', 'bloqueado')
    list_filter = ('bloqueado', 'estado', 'cidade')
    search_fields = ('nome', 'cpf', 'email', 'telefone')
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('nome', 'cpf', 'rg', 'passaporte', 'cnh', 'data_nascimento', 'nacionalidade', 'uf_nascimento')
        }),
        ('Contato', {
            'fields': ('telefone', 'email')
        }),
        ('Endereço', {
            'fields': ('endereco', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'cep')
        }),
        ('Informações Profissionais', {
            'fields': ('profissao', 'renda')
        }),
        ('Estado Civil', {
            'fields': ('estado_civil', 'uniao')
        }),
        ('Outras Informações', {
            'fields': ('bloqueado', 'observacao')
        }),
    )

@admin.register(Uniao)
class UniaoAdmin(admin.ModelAdmin):
    list_display = ('cliente1', 'cliente2', 'data_uniao', 'regime_uniao')
    search_fields = ('cliente1__nome', 'cliente2__nome')
    list_filter = ('regime_uniao',)

@admin.register(Carteira)
class CarteiraAdmin(admin.ModelAdmin):
    list_display = ('corretor', 'origem', 'ticket', 'tipo')
    list_filter = ('corretor', 'tipo', 'regiao')
    search_fields = ('corretor__username', 'ticket', 'regiao')
    filter_horizontal = ('clientes',)
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('clientes', 'corretor', 'origem', 'ticket')
        }),
        ('Detalhes do Imóvel', {
            'fields': ('metragem', 'regiao', 'quartos', 'banheiros', 'vagas', 'tipo')
        }),
    )

@admin.register(OfertaAtiva)
class OfertaAtivaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'corretor', 'tipo', 'resultado')
    list_filter = ('tipo', 'resultado')
    search_fields = ('cliente__nome', 'corretor__username')
    date_hierarchy = 'criado'
