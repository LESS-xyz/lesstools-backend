from django.contrib import admin
from lesstools.analytics.models import Token, Pair, UserPairVote


class PairAdmin(admin.ModelAdmin):
    search_fields = ['address']


class TokenAdmin(admin.ModelAdmin):
    search_fields = ['id', 'cmc_id', 'cmc_slug', 'eth_address', 'bsc_address', 'polygon_address']


# Register your models here.
admin.site.register(Token, TokenAdmin)
admin.site.register(Pair, PairAdmin)
admin.site.register(UserPairVote)
