# Generated by Django 5.2.3 on 2025-06-21 05:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_alter_formulariofield_default_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='formulariosubmission',
            name='user_agent',
            field=models.TextField(blank=True, verbose_name='User Agent'),
        ),
        migrations.AddField(
            model_name='formulariosubmission',
            name='user_ip',
            field=models.GenericIPAddressField(blank=True, null=True, verbose_name='IP do usuário'),
        ),
        migrations.AlterField(
            model_name='formulariofield',
            name='default_value',
            field=models.CharField(blank=True, help_text='Valor pré-preenchido (opcional)', max_length=255, verbose_name='Valor padrão'),
        ),
    ]
