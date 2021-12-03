import logging

from web3 import Web3

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lesstools.accounts.models import AdvUser
from lesstools.analytics.models import Pair, UserPairVote
from lesstools.analytics.serializers import PairSerializer, UserPairVoteSerializer
from lesstools.settings import SWAP

from lesstools.analytics.api import mapping_update, info_from_cmc, info_from_ethplorer, try_extend_if_needed, candles_creater

CMC_PAGE_SIZE = 10000


@swagger_auto_schema(
    method='post',
    operation_description="Manual update of CoinMarketCap IDs map."
                          "Make full update if need to update also existing entities",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'run_full_update': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        },
    ),
    responses={'200': 'Mapping updated',
               '401': 'Only for admins usage',
               '503': 'CoinMarketCap API unavailable'}
)
@api_view(http_method_names=['POST'])
@permission_classes([IsAdminUser])
def manual_cmc_mapping_update(request):
    run_full_update: bool = bool(request.data['run_full_update'])

    try:
        mapping_update(run_full_update)
    except RuntimeError:
        return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)

    return Response('Mapping updated', status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Retrieve additional pair info.\n"
                          "Field 'vote' can be 0 in both cases of a neutral vote or unauthorized retrieval",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'pair_address': openapi.Schema(type=openapi.TYPE_STRING),
            'token_address': openapi.Schema(type=openapi.TYPE_STRING),
            'token_name': openapi.Schema(type=openapi.TYPE_STRING),
            'token_symbol': openapi.Schema(type=openapi.TYPE_STRING),
            'platform': openapi.Schema(type=openapi.TYPE_STRING, enum=['ETH', 'BSC', 'POLYGON', 'XDAI', 'AVALANCHE', 'FANTOM']),
        },
        required=['pair_address', 'token_address', 'token_name', 'token_symbol', 'platform']
    ),
    responses={'200': UserPairVoteSerializer()}
)
@api_view(http_method_names=['POST'])
def pair_info_retrieval(request):
    try:
        user_address = Web3.toChecksumAddress(request.user.username)
    # if it's anonymous user or the one without hex-string username (e.g. admins)
    except ValueError:
        logging.info(f'not authenticated or admin user is retrieving information ({request.user} in this case)')
        user_address = None

    pair_address = Web3.toChecksumAddress(request.data['pair_address'])
    token_address = Web3.toChecksumAddress(request.data['token_address'])
    token_name = request.data['token_name']
    token_symbol = request.data['token_symbol']
    platform = request.data['platform'].upper()

    token_info = info_from_cmc(token_address, token_name, token_symbol, platform)

    if token_info is not None:
        token_info = try_extend_if_needed(token_info, platform)
    elif platform == 'ETH':
        token_info = info_from_ethplorer(token_address)
    else:
        logging.info('No information is available for specified token')
        token_info = None

    pair_info, created = Pair.objects.get_or_create(address=pair_address,
                                                    platform=platform,
                                                    defaults={'token_being_reviewed': token_info})

    if created:
        logging.info(f'pair "{pair_info.address}" on {pair_info.platform} platform saved to the database')
    else:
        # if analytics are requested for another token in this pair
        pair_info.token_being_reviewed = token_info
        pair_info.save()

    if user_address is not None:
        user_pair_vote_filter = UserPairVote.objects.filter(user__username__iexact=user_address,
                                                            pair__address__iexact=pair_address)
        if user_pair_vote_filter.exists():
            return Response(UserPairVoteSerializer(user_pair_vote_filter.first(),
                                                   context={'username': user_address}).data)

    # for the uniformity of the server response
    return Response({'pair': PairSerializer(pair_info, context={'username': user_address}).data,
                     'vote': 0})


@swagger_auto_schema(
    method='post',
    operation_description="Like or dislike the pair ot change the community trust.\n"
                          "It's also possible to cancel vote if the sent vote equals the one saved to the DB",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'pair_address': openapi.Schema(type=openapi.TYPE_STRING),
            'platform': openapi.Schema(type=openapi.TYPE_STRING, enum=['ETH', 'BSC', 'POLYGON', 'FANTOM', 'XDAI', 'AVALANCHE']),
            'vote': openapi.Schema(type=openapi.TYPE_INTEGER, enum=[-1, 1]),
        },
        required=['pair_address', 'vote']
    ),
    responses={'200': UserPairVoteSerializer(),
               '403': 'Invalid authentication (no such user in the DB)',
               '404': 'No such pair in the DB',
               '406': 'Unsupported user type for this operation'}
)
@api_view(http_method_names=['POST'])
@permission_classes([IsAuthenticated])
def pair_vote(request):
    try:
        user_address = Web3.toChecksumAddress(request.user.username)
    # if it's a user without hex-string username (e.g. admins)
    except ValueError:
        logging.error(f'unsupported type of user is trying to vote ({request.user} in this case)')
        return Response('Unsupported user type for this operation', status=status.HTTP_406_NOT_ACCEPTABLE)

    pair_address = Web3.toChecksumAddress(request.data['pair_address'])
    platform = request.data['platform'].upper()
    vote = request.data['vote']

    user_filter = AdvUser.objects.filter(username__iexact=user_address)
    if not user_filter.exists():
        return Response(f'No user {user_address} record in the database', status=status.HTTP_403_FORBIDDEN)

    pair_filter = Pair.objects.filter(address=pair_address, platform=platform)
    if not pair_filter.exists():
        return Response(f'No pair {pair_address} record in the database', status=status.HTTP_404_NOT_FOUND)

    user = user_filter.first()
    pair = pair_filter.first()
    user_pair_vote, created = UserPairVote.objects.get_or_create(user__username__iexact=user_address,
                                                                 pair__address__iexact=pair_address,
                                                                 defaults={'user': user,
                                                                           'pair': pair})
    if created:
        user_pair_vote.vote = vote
        user_pair_vote.save()
    else:
        user_pair_vote.vote = UserPairVote.NEUTRAL if user_pair_vote.vote == vote else vote
        user_pair_vote.save()

    return Response(UserPairVoteSerializer(user_pair_vote, context={'username': user_address}).data)


graph_response = openapi.Response(
    description='Values for candles graph',
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'start_time': openapi.Schema(type=openapi.TYPE_INTEGER),
            'end_time': openapi.Schema(type=openapi.TYPE_INTEGER),
            'open': openapi.Schema(type=openapi.TYPE_STRING),
            'close': openapi.Schema(type=openapi.TYPE_STRING),
            'high': openapi.Schema(type=openapi.TYPE_STRING),
            'low': openapi.Schema(type=openapi.TYPE_STRING),
        }
    )
)


class Candles(APIView):
    @swagger_auto_schema(
        operation_description="Graph candle info",
        responses={200: graph_response}
    )
    def get(self, request, pair_id, pool, time_interval, candles):
        graph_response = candles_creater(pair_id=pair_id, url=SWAP[pool], time_interval=time_interval, candles=candles)
        if graph_response == {'error': 'Pair not found'}:
            return Response(graph_response, status=status.HTTP_404_NOT_FOUND)
        elif graph_response == {'error': 'api not reach'}:
            return Response(graph_response, status=status.HTTP_504_GATEWAY_TIMEOUT)
        return Response(graph_response, status=status.HTTP_200_OK)
