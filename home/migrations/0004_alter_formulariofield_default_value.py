# Generated by Django 5.2.3 on 2025-06-21 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_formulariopage_formulariofield_formulariosubmission_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formulariofield',
            name='default_value',
            field=models.TextField(blank=True, help_text='Default value. Comma or new line separated values supported for checkboxes.', verbose_name='default value'),
        ),
    ]
