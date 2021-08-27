# Generated by Django 3.2.6 on 2021-08-27 16:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('networks', '0011_auto_20210825_1512'),
        ('accounts', '0012_auto_20210825_1423'),
    ]

    operations = [
        migrations.AddField(
            model_name='planpayment',
            name='grants_plan',
            field=models.CharField(choices=[('Free', 'Free'), ('Standard', 'Standard'), ('Premium', 'Premium')], default='Free', help_text='"Free" means that payment was unsuccessful', max_length=10),
        ),
        migrations.CreateModel(
            name='UserHolding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('less_holding_amount', models.DecimalField(decimal_places=18, max_digits=78, null=True)),
                ('network', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='holdings', to='networks.network')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='holds', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'network')},
            },
        ),
    ]
