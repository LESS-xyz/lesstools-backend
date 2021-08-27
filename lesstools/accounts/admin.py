from django.contrib import admin
from lesstools.accounts import models


class PlanPaymentAdmin(admin.ModelAdmin):
    readonly_fields = ('payment_time', 'grants_plan')


class AdvUserAdmin(admin.ModelAdmin):
    readonly_fields = ('holdings', 'password')

    @admin.display(description='User LESS holdings in supported networks')
    def holdings(self, instance):
        return {holding.network.name: float(holding.less_holding_amount) for holding in instance.holds.all()}


admin.site.register(models.PlanPrice)
admin.site.register(models.AdvUser, AdvUserAdmin)
admin.site.register(models.PlanPayment, PlanPaymentAdmin)
