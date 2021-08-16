from django.contrib import admin
from lesstools.analytics.models import Token, Pair, UserPairVote

# Register your models here.
admin.site.register(Token)
admin.site.register(Pair)
admin.site.register(UserPairVote)
