# Generated by Django 3.2.3 on 2021-08-06 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Pairs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trust', models.PositiveSmallIntegerField(auto_created=True, default=0, editable=False)),
                ('main_currency', models.CharField(max_length=4)),
                ('sub_currency', models.CharField(max_length=4)),
                ('rating', models.DecimalField(decimal_places=2, default=0.0, editable=False, max_digits=3)),
                ('likes', models.PositiveSmallIntegerField(default=0, editable=False)),
                ('dislikes', models.PositiveSmallIntegerField(default=0, editable=False)),
            ],
        ),
    ]
