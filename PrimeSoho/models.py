from django.db import models

class core(models.Model):
    criado = models.DateTimeField('Data de criação', auto_now_add=True, editable=False)
    modificado = models.DateTimeField('Data de modificação', auto_now=True)
    ativo = models.BooleanField('Ativo', default=True)

    def save(self, *args, **kwargs):
        for field in self._meta.fields:
            if isinstance(field, models.DateTimeField) or isinstance(field, models.TimeField):
                value = getattr(self, field.name)
                if value:
                    setattr(self, field.name, value.replace(second=0, microsecond=0))
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
