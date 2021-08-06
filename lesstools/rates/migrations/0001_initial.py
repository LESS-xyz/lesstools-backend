# Generated by Django 3.2.3 on 2021-06-29 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UsdRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(max_length=100)),
                ('rate', models.DecimalField(decimal_places=2, max_digits=78, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]