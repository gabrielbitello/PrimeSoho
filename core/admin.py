from django.contrib import admin

from .models import Token_Recuperar_Senha


@admin.register(Token_Recuperar_Senha)
class Token_Recuperar_SenhaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'token', 'data_utilizacao', 'ativo']
    search_fields = ['usuario', 'token']
    list_filter = ['ativo']