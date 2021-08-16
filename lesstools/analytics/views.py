from web3 import Web3

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from rest_framework.response import Response

from lesstools.analytics.serializers import TokenSerializer

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
    operation_description="Retrieve additional pair info",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'token_address': openapi.Schema(type=openapi.TYPE_STRING),
            'token_name': openapi.Schema(type=openapi.TYPE_STRING),
            'token_symbol': openapi.Schema(type=openapi.TYPE_STRING),
            'platform': openapi.Schema(type=openapi.TYPE_STRING, enum=['ETH', 'BSC', 'POLYGON']),
        },
        required=['token_address', 'token_name', 'token_symbol', 'platform']
    ),
    responses={'200': TokenSerializer(),
               '501': 'No information is available for specified token',
               '503': 'External API unavailable'}
)
@api_view(http_method_names=['POST'])
def pair_info_retrieval(request):
    # pair_address = request.data['pair_address'] do we need it?
    token_address = Web3.toChecksumAddress(request.data['token_address'])
    token_name = request.data['token_name']
    token_symbol = request.data['token_symbol']
    platform = request.data['platform'].upper()

    try:
        info = info_from_cmc(token_address, token_name, token_symbol, platform)
    except RuntimeError:
        return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE, data='CoinMarketCap API unavailable')

    if info is not None:
        try:
            info = try_extend_if_needed(info, platform)
        except RuntimeError as err:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE, data=err.args)
        return Response(TokenSerializer(info).data)
    elif platform == 'ETH':
        try:
            info = info_from_ethplorer(token_address)
            return Response(TokenSerializer(info).data)
        except RuntimeError:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE, data='Ethplorer API unavailable')
    else:
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED, data='No information is available for specified token')
