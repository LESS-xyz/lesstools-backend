from typing import Union

from web3 import Web3

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from rest_framework.response import Response

from lesstools.accounts.models import AdvUser
from lesstools.analytics.models import Pair, UserPairVote
from lesstools.analytics.serializers import TokenSerializer, PairSerializer, UserPairVoteSerializer, \
    ResponseUnionExampleSerializer

from lesstools.analytics.api import mapping_update, info_from_cmc, info_from_ethplorer, try_extend_if_needed

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
                          "If response body has 'vote' field then there is info about the vote of the current user.\n"
                          "If there is no such field - the format of response is different: pair info is not nested.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'user_address': openapi.Schema(type=openapi.TYPE_STRING),
            'pair_address': openapi.Schema(type=openapi.TYPE_STRING),
            'token_address': openapi.Schema(type=openapi.TYPE_STRING),
            'token_name': openapi.Schema(type=openapi.TYPE_STRING),
            'token_symbol': openapi.Schema(type=openapi.TYPE_STRING),
            'platform': openapi.Schema(type=openapi.TYPE_STRING, enum=['ETH', 'BSC', 'POLYGON']),
        },
        required=['pair_address', 'token_address', 'token_name', 'token_symbol', 'platform']
    ),
    responses={'200': ResponseUnionExampleSerializer()}
)
@api_view(http_method_names=['POST'])
def pair_info_retrieval(request):
    user_address = Web3.toChecksumAddress(request.data['user_address']) if 'user_address' in request.data else None
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
        print('No information is available for specified token')
        token_info = None

    pair_info, created = Pair.objects.get_or_create(address=pair_address,
                                                    platform=platform,
                                                    defaults={'token_being_reviewed': token_info})

    if created:
        print(f'pair "{pair_info.address}" on {pair_info.platform} platform saved to the database')

    if user_address is not None:
        user_pair_vote_filter = UserPairVote.objects.filter(user__username__iexact=user_address,
                                                            pair__address__iexact=pair_address)
        if user_pair_vote_filter.exists():
            return Response(UserPairVoteSerializer(user_pair_vote_filter.first()).data)

    return Response(PairSerializer(pair_info).data)
