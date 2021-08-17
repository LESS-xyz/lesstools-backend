from rest_framework import serializers
from . import models
from .models import UserPairVote


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Token
        fields = ('cmc_id', 'cmc_slug', 'name', 'symbol', 'total_supply', 'circulating_supply', 'holders_count',
                  'eth_address', 'bsc_address', 'polygon_address',
                  'website_url', 'chat_urls', 'twitter_url')


class PairSerializer(serializers.ModelSerializer):
    token_being_reviewed = TokenSerializer()
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()

    class Meta:
        model = models.Pair
        fields = ('address', 'platform', 'likes', 'dislikes', 'token_being_reviewed')

    def get_likes(self, obj):
        return obj.votes.filter(vote=UserPairVote.LIKE).count()

    def get_dislikes(self, obj):
        return obj.votes.filter(vote=UserPairVote.DISLIKE).count()


class UserPairVoteSerializer(serializers.ModelSerializer):
    pair = PairSerializer()

    class Meta:
        model = models.UserPairVote
        fields = ('pair', 'vote')


# for visible union of possible responses
class ResponseUnionExampleSerializer(serializers.Serializer):
    pair_serializer = PairSerializer(many=True, required=False)
    user_pair_vote_serializer = UserPairVoteSerializer(many=True, required=False)
