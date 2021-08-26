from django.contrib import admin
from django import forms
from . import models

from web3 import Web3


class NetworkForm(forms.ModelForm):
    class Meta:
        model = models.Network
        fields = '__all__'

    def clean(self):
        allows_holding = self.cleaned_data.get('allows_holding_for_paid_plans')
        less_token_address = self.cleaned_data.get('less_token_address')

        if allows_holding:
            if less_token_address is None:
                raise forms.ValidationError("LESS token address can't be empty if holding is allowed")
            else:
                try:
                    Web3.toChecksumAddress(less_token_address)
                except ValueError:
                    raise forms.ValidationError("Provided address is not a valid hex string")

        return self.cleaned_data


class NetworkAdmin(admin.ModelAdmin):
    form = NetworkForm


# Register your models here.
admin.site.register(models.Network, NetworkAdmin)
admin.site.register(models.PaymentToken)
