# Generated by Django 5.1.1 on 2024-10-31 20:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0014_alter_order_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['pk']},
        ),
    ]
