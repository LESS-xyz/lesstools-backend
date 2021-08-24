from django.contrib import admin
from lesstools.accounts import models


class PlanPaymentAdmin(admin.ModelAdmin):
    readonly_fields = ('payment_time', )


admin.site.register(models.PlanPrice)
admin.site.register(models.AdvUser)
admin.site.register(models.PlanPayment, PlanPaymentAdmin)
