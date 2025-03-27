from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from PrimeSoho.models import core
from clientes.models import Cliente, Carteira

class Imoveis(core):
    endereco = models.CharField(_('Endereço'), max_length=255)
    numero = models.CharField(_('Número'), max_length=10)
    nome_aglomerado = models.CharField(_('Nome do aglomerado'), max_length=255, blank=True, null=True)
    complemento = models.CharField(_('Complemento'), max_length=255, blank=True, null=True)
    bairro = models.CharField(_('Bairro'), max_length=255)
    cidade = models.CharField(_('Cidade'), max_length=255)
    estado = models.CharField(_('Estado'), max_length=2)
    cep = models.CharField(_('CEP'), max_length=10)
    descricao = models.TextField(_('Descrição'), blank=True, null=True)
    valor = models.DecimalField(_('Valor'), max_digits=14, decimal_places=2)
    area_total = models.DecimalField(_('Área total'), max_digits=10, decimal_places=2, blank=True, null=True)
    area_privativa = models.DecimalField(_('Área privativa'), max_digits=10, decimal_places=2, blank=True, null=True)
    quartos = models.PositiveIntegerField(_('Quartos'), blank=True, null=True)
    banheiros = models.PositiveIntegerField(_('Banheiros'), blank=True, null=True)
    garagem = models.PositiveIntegerField(_('Garagem'), blank=True, null=True)
    suites = models.PositiveIntegerField(_('Suítes'), blank=True, null=True)
    lavabos = models.PositiveIntegerField(_('Lavabos'), blank=True, null=True)
    salas = models.PositiveIntegerField(_('Salas'), blank=True, null=True)
    tipo = models.CharField(_('Tipo'), max_length=255, blank=True, null=True)
    
    # Campos booleanos
    area_servico = models.BooleanField(_('Área de serviço'), default=False)
    sacada = models.BooleanField(_('Sacada'), default=False)
    churrasqueira = models.BooleanField(_('Churrasqueira'), default=False)
    piscina = models.BooleanField(_('Piscina'), default=False)
    academia = models.BooleanField(_('Academia'), default=False)
    salao_festas = models.BooleanField(_('Salão de festas'), default=False)
    playground = models.BooleanField(_('Playground'), default=False)
    quadra = models.BooleanField(_('Quadra'), default=False)
    lavanderia = models.BooleanField(_('Lavanderia'), default=False)
    mobiliado = models.BooleanField(_('Mobiliado'), default=False)
    destaque = models.BooleanField(_('Destaque'), default=False)
    
    imagems = models.ImageField(_('Imagens'), upload_to='imoveis', blank=True, null=True)
    angariador = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Angariador'), on_delete=models.SET_NULL, null=True, blank=True)
    indicador = models.CharField(_('Indicador'), max_length=255, blank=True, null=True)
    porcentagem = models.DecimalField(_('Porcentagem'), max_digits=5, decimal_places=2)
    ref = models.CharField(_('Ref'), max_length=255, blank=True, null=True)
    proprietario = models.ManyToManyField(Cliente, related_name='imoveis_proprietarios', verbose_name=_('Proprietários'))
    divulgar = models.BooleanField(_('Divulgar'), default=True)
    condicoes_pagamento = models.TextField(_('Condições de pagamento'), blank=True, null=True)
    documentos = models.TextField(_('Documentos'), blank=True, null=True)
    matricula = models.CharField(_('Matrícula'), max_length=255, blank=True, null=True)
    indicacao_fiscal = models.CharField(_('Indicação fiscal'), max_length=255, blank=True, null=True)
    valor_condominio = models.DecimalField(_('Valor do condomínio'), max_digits=10, decimal_places=2, blank=True, null=True)
    andar = models.PositiveIntegerField(_('Andar'), blank=True, null=True)
    elevador = models.BooleanField(_('Elevador'), default=False)
    portaria = models.BooleanField(_('Portaria'), default=False)
    exclusividade = models.BooleanField(_('Exclusividade'), default=False)
    tempo_exclusividade = models.PositiveIntegerField(_('Tempo de exclusividade'), blank=True, null=True)
    iptu = models.DecimalField(_('IPTU'), max_digits=10, decimal_places=2, blank=True, null=True)
    chave = models.CharField(_('Chave'), max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.endereco}, {self.numero}, {self.complemento} - {self.bairro}, {self.cidade}"

    class Meta:
        verbose_name = _('Imóvel')
        verbose_name_plural = _('Imóveis')
        ordering = ['endereco']

class Visita(core):
    cliente = models.ForeignKey(Carteira, verbose_name=_('Cliente'), related_name='visitas', on_delete=models.SET_NULL, null=True)
    imovel = models.ForeignKey(Imoveis, verbose_name=_('Imóvel'), related_name='visitas', on_delete=models.SET_NULL, null=True)
    data_visita = models.DateTimeField(_('Data da visita'))    
    confirmacao = models.BooleanField(_('Confirmação'), default=False)

    def save(self, *args, **kwargs):
        if self.cliente:
            self.cliente.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cliente} - {self.imovel} - {self.data_visita}"

    class Meta:
        verbose_name = _('Visita')
        verbose_name_plural = _('Visitas')
        ordering = ['data_visita']

class Proposta(core):
    cliente = models.ForeignKey(Carteira, verbose_name=_('Cliente'), related_name='propostas', on_delete=models.SET_NULL, null=True)
    imovel = models.ForeignKey(Imoveis, verbose_name=_('Imóvel'), related_name='propostas', on_delete=models.SET_NULL, null=True)
    data_proposta = models.DateTimeField(_('Data da proposta'))
    valor_proposta = models.DecimalField(_('Valor da proposta'), max_digits=10, decimal_places=2)
    entrada = models.DecimalField(_('Entrada'), max_digits=10, decimal_places=2, blank=True, null=True)
    tipo_entrada = models.CharField(_('Tipo de entrada'), max_length=255, blank=True, null=True)
    financiamento = models.DecimalField(_('Financiamento'), max_digits=10, decimal_places=2, blank=True, null=True)
    fgts = models.DecimalField(_('FGTS'), max_digits=10, decimal_places=2, blank=True, null=True)
    sinal = models.DecimalField(_('Sinal'), max_digits=10, decimal_places=2, blank=True, null=True)
    tipo_sinal = models.CharField(_('Tipo de sinal'), max_length=255, blank=True, null=True)
    imovel_troca = models.ForeignKey(Imoveis, verbose_name=_('Imóvel na troca'), related_name='propostas_troca', on_delete=models.SET_NULL, blank=True, null=True)
    veiculo_troca = models.CharField(_('Veículo na troca'), max_length=600, blank=True, null=True)
    condicao_entrega = models.CharField(_('Condição de entrega'), max_length=255, blank=True, null=True)
    ficam_no_imovel = models.TextField(_('Ficam no imóvel'), blank=True, null=True)
    observacao = models.TextField(_('Observação'), blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.cliente:
            self.cliente.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cliente} - {self.imovel} - {self.data_proposta}"

    class Meta:
        verbose_name = _('Proposta')
        verbose_name_plural = _('Propostas')
        ordering = ['data_proposta']