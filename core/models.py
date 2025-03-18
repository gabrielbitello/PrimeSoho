from django.db import models
from PrimeSoho.models import core

class Token_Recuperar_Senha(core):
    usuario = models.CharField('Usuario', max_length=255, editable=False)
    token = models.CharField('Token', max_length=255, editable=False)
    data_utilizacao = models.DateTimeField('Data de utilização', null=True, blank=True)

    def __str__(self):
        return self.usuario

    class Meta:
        verbose_name = 'Token de recuperação de senha'
        verbose_name_plural = 'Tokens de recuperação de senha'
        ordering = ['usuario']
