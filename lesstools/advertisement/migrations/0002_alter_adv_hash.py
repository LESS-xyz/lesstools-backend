# Generated by Django 3.2.6 on 2021-08-19 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advertisement', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adv',
            name='hash',
            field=models.CharField(blank=True, max_length=256),
        ),
    ]