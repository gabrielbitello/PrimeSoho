# Generated by Django 5.1.7 on 2025-03-27 05:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imoveis', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='imoveis',
            name='chave',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Chave'),
        ),
        migrations.AddField(
            model_name='imoveis',
            name='tipo',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Tipo'),
        ),
    ]
