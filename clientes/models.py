from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from PrimeSoho.models import core

class Cliente(core):
    nome = models.CharField(_('Nome'), max_length=255)
    cpf = models.CharField(_('CPF'), max_length=14, blank=True, null=True)
    rg = models.CharField(_('RG'), max_length=14, blank=True, null=True)
    passaporte = models.CharField(_('Passaporte'), max_length=255, blank=True, null=True)
    cnh = models.CharField(_('CNH'), max_length=255, blank=True, null=True)
    data_nascimento = models.DateField(_('Data de nascimento'), blank=True, null=True)
    telefone = models.CharField(_('Telefone'), max_length=20)
    email = models.EmailField(_('E-mail'), max_length=255)
    endereco = models.CharField(_('Endereço'), max_length=255, blank=True, null=True)
    numero = models.CharField(_('Número'), max_length=10, blank=True, null=True)
    complemento = models.CharField(_('Complemento'), max_length=255, blank=True, null=True)
    bairro = models.CharField(_('Bairro'), max_length=255, blank=True, null=True)
    cidade = models.CharField(_('Cidade'), max_length=255, blank=True, null=True)
    estado = models.CharField(_('Estado'), max_length=2, blank=True, null=True)
    cep = models.CharField(_('CEP'), max_length=10, blank=True, null=True)
    bloqueado = models.BooleanField(_('Bloqueado'), default=False)
    profissao = models.CharField(_('Profissão'), max_length=255, blank=True, null=True)
    renda = models.DecimalField(_('Renda'), max_digits=10, decimal_places=2, blank=True, null=True)
    estado_civil = models.CharField(_('Estado civil'), max_length=255, blank=True, null=True)
    uniao = models.ForeignKey('Uniao', verbose_name=_('União'), on_delete=models.SET_NULL, blank=True, null=True)
    observacao = models.TextField(_('Observação'), blank=True, null=True)
    nacionalidade = models.CharField(_('Nacionalidade'), max_length=255, blank=True, null=True)
    uf_nascimento = models.CharField(_('UF de nascimento'), max_length=2, blank=True, null=True)

    def __str__(self):
        return f'{self.nome} - {self.cpf or "CPF não informado"}'

    class Meta:
        verbose_name = _('Cliente')
        verbose_name_plural = _('Clientes')
        ordering = ['nome']

class Uniao(core):
    cliente1 = models.ForeignKey(Cliente, verbose_name=_('Cliente 1'), related_name='unioes_como_cliente1', on_delete=models.SET_NULL, null=True)
    cliente2 = models.ForeignKey(Cliente, verbose_name=_('Cliente 2'), related_name='unioes_como_cliente2', on_delete=models.SET_NULL, null=True)
    data_uniao = models.DateField(_('Data de união'), blank=True, null=True)
    regime_uniao = models.CharField(_('Regime de união'), max_length=255)

    def save(self, *args, **kwargs):
        # Salva a união primeiro
        super().save(*args, **kwargs)

        # Atualiza o campo 'uniao' dos clientes associados
        if self.cliente1:
            self.cliente1.uniao = self
            self.cliente1.save()
        
        if self.cliente2:
            self.cliente2.uniao = self
            self.cliente2.save()

    def __str__(self):
        return f'{self.cliente1} - {self.cliente2}'

    class Meta:
        verbose_name = _('União')
        verbose_name_plural = _('Uniões')

class Carteira(core):
    clientes = models.ManyToManyField(Cliente, related_name='carteiras', verbose_name=_('Clientes'))
    corretor = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Corretor'), on_delete=models.SET_NULL, blank=True, null=True)
    origem = models.CharField(_('Origem'), max_length=255, blank=True, null=True)
    ticket = models.CharField(_('Ticket'), max_length=255, blank=True, null=True)
    metragem = models.DecimalField(_('Metragem'), max_digits=10, decimal_places=2, blank=True, null=True)
    regiao = models.CharField(_('Região'), max_length=255, blank=True, null=True)
    quartos = models.PositiveIntegerField(_('Quartos'), blank=True, null=True)
    banheiros = models.PositiveIntegerField(_('Banheiros'), blank=True, null=True)
    vagas = models.PositiveIntegerField(_('Vagas'), blank=True, null=True)
    tipo = models.CharField(_('Tipo'), max_length=255, blank=True, null=True)

    def __str__(self):
        return f'Carteira de {self.corretor or "Corretor não atribuído"}'

    class Meta:
        verbose_name = _('Carteira')
        verbose_name_plural = _('Carteiras')

class OfertaAtiva(core):
    cliente = models.ForeignKey(Cliente, verbose_name=_('Cliente'), on_delete=models.SET_NULL, null=True)
    corretor = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Corretor'), on_delete=models.SET_NULL, null=True)
    tipo = models.CharField(_('Tipo'), max_length=255)
    resultado = models.CharField(_('Resultado'), max_length=255)

    def __str__(self):
        return f'Oferta de {self.cliente} por {self.corretor}'

    class Meta:
        verbose_name = _('Oferta Ativa')
        verbose_name_plural = _('Ofertas Ativas')
        ordering = ['-criado']