from rest_framework import serializers
from . import models
from .models import UserPairVote


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Token
        fields = ('cmc_id', 'cmc_slug', 'name', 'symbol', 'total_supply', 'circulating_supply', 'holders_count',
                  'eth_address', 'bsc_address', 'polygon_address', 'fantom_address', 'xdai_address', 'avalanche_address',
                  'website_url', 'chat_urls', 'twitter_url')


class PairSerializer(serializers.ModelSerializer):
    token_being_reviewed = TokenSerializer()
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()

    is_favourite_of_current_user = serializers.SerializerMethodField('_is_favourite')

    class Meta:
        model = models.Pair
        fields = ('address', 'platform', 'likes', 'dislikes', 'token_being_reviewed', 'is_favourite_of_current_user')

    def get_likes(self, obj):
        return obj.votes.filter(vote=UserPairVote.LIKE).count()

    def get_dislikes(self, obj):
        return obj.votes.filter(vote=UserPairVote.DISLIKE).count()

    # check is current pair is favourite for the current user
    def _is_favourite(self, obj):
        username = self.context.get('username')
        if username is not None:
            return obj.favourite_of.filter(username__iexact=username).exists()
        else:
            return False


class UserPairVoteSerializer(serializers.ModelSerializer):
    pair = PairSerializer()

    class Meta:
        model = models.UserPairVote
        fields = ('pair', 'vote')
