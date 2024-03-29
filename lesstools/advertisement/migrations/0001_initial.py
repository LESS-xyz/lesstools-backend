# Generated by Django 3.2.6 on 2021-08-19 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ADV',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=32)),
                ('sub_name', models.CharField(blank=True, max_length=32)),
                ('icon', models.ImageField(upload_to='media/img-%Y-%m-%d/')),
                ('description', models.CharField(blank=True, max_length=128)),
                ('position', models.CharField(choices=[('TOP', 'top'), ('MID', 'mid'), ('BOT', 'bot')], default='MID', max_length=3)),
                ('hash', models.CharField(blank=True, editable=False, max_length=256)),
            ],
        ),
    ]
