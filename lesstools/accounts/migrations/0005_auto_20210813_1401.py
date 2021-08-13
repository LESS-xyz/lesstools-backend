# Generated by Django 3.2.6 on 2021-08-13 14:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pairs', '0002_remove_pairs_rating'),
        ('accounts', '0004_alter_advuser_favourite_pairs'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlanPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.PositiveSmallIntegerField(help_text='You can have only one price object, and can not delete this object')),
            ],
        ),
    ]
