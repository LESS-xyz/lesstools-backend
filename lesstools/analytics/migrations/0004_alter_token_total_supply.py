# Generated by Django 3.2.3 on 2021-08-12 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0003_auto_20210811_1558'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='total_supply',
            field=models.DecimalField(decimal_places=0, max_digits=100, null=True),
        ),
    ]
