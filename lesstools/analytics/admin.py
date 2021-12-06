from django.contrib import admin
from lesstools.analytics.models import Token, Pair, UserPairVote, HotPairManager, MainToken


class PairAdmin(admin.ModelAdmin):
    search_fields = ['address']


class TokenAdmin(admin.ModelAdmin):
    search_fields = ['id', 'cmc_id', 'cmc_slug', 'eth_address', 'bsc_address', 'polygon_address', 'fantom_address', 'xdai_address', 'avalanche_address']


class UserPairVoteAdmin(admin.ModelAdmin):
    readonly_fields = ('vote',)


# Register your models here.
admin.site.register(Token, TokenAdmin)
admin.site.register(Pair, PairAdmin)
admin.site.register(UserPairVote, UserPairVoteAdmin)
admin.site.register(HotPairManager)
admin.site.register(MainToken)
