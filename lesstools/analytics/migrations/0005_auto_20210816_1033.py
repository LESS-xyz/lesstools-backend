# Generated by Django 3.2.6 on 2021-08-16 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0004_alter_token_total_supply'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='bsc_address',
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='token',
            name='eth_address',
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='token',
            name='polygon_address',
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
    ]
