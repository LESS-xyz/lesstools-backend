from rest_framework import serializers
from . import models


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Token
        fields = ('cmc_id', 'cmc_slug', 'name', 'symbol', 'total_supply', 'circulating_supply', 'holders_count',
                  'eth_address', 'bsc_address', 'polygon_address',
                  'website_url', 'chat_urls', 'twitter_url')


class PairSerializer(serializers.ModelSerializer):
    token_being_reviewed = TokenSerializer()

    class Meta:
        model = models.Pair
        fields = ('address', 'platform', 'likes', 'dislikes', 'token_being_reviewed')


class UserPairVoteSerializer(serializers.ModelSerializer):
    pair = PairSerializer()

    class Meta:
        model = models.UserPairVote
        fields = ('pair', 'vote')


# for visible union of possible responses
class ResponseUnionExampleSerializer(serializers.Serializer):
    pair_serializer = PairSerializer(many=True, required=False)
    user_pair_vote_serializer = UserPairVoteSerializer(many=True, required=False)
