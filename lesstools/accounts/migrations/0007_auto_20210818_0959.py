# Generated by Django 3.2.6 on 2021-08-18 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0007_auto_20210817_1416'),
        ('accounts', '0006_auto_20210816_1630'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='advuser',
            name='favourite_pairs',
        ),
        migrations.AddField(
            model_name='advuser',
            name='favourite_pairs',
            field=models.ManyToManyField(blank=True, related_name='favourite_of', to='analytics.Pair'),
        ),
    ]
