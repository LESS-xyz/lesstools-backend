# Generated by Django 3.2.6 on 2021-08-23 14:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rates', '0001_initial'),
        ('networks', '0004_alter_network_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=128)),
                ('currency', models.CharField(max_length=100, unique=True)),
                ('coingecko_code', models.CharField(max_length=100)),
                ('decimals', models.IntegerField(default=18)),
            ],
        ),
        migrations.RemoveField(
            model_name='network',
            name='native_decimals',
        ),
        migrations.DeleteModel(
            name='Token',
        ),
        migrations.AddField(
            model_name='paymenttoken',
            name='network',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='networks.network'),
        ),
        migrations.AddField(
            model_name='paymenttoken',
            name='usd_rate',
            field=models.OneToOneField(on_delete=django.db.models.deletion.RESTRICT, to='rates.usdrate'),
        ),
        migrations.AddField(
            model_name='network',
            name='native_token',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='NOT_NEEDED+', to='networks.paymenttoken'),
        ),
    ]
