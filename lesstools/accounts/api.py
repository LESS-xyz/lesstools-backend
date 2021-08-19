from random import choice
from string import ascii_letters

from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from web3 import Web3
from eth_utils.hexadecimal import add_0x_prefix
from eth_account.messages import encode_defunct
from eth_account import Account

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import status
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from lesstools.accounts.models import PlanPrice, AdvUser

import logging

from lesstools.analytics.models import Pair
from lesstools.settings import FAVOURITE_PAIRS_LIMIT


def valid_metamask_message(address, message, signature):

    r = int(signature[0:66], 16)
    s = int(add_0x_prefix(signature[66:130]), 16)
    v = int(add_0x_prefix(signature[130:132]), 16)
    if v not in (27, 28):
        v += 27

    message_hash = encode_defunct(text=message)
    signer_address = Account.recover_message(message_hash, vrs=(v, r, s))
    logging.info(signer_address)
    logging.info(address)

    if signer_address.lower() != address.lower():
        raise ValidationError({'result': 'Incorrect signature'}, code=400)
    return True


@api_view(http_method_names=['GET'])
def generate_metamask_message(request):

    generated_message = ''.join(choice(ascii_letters) for ch in range(30))
    request.session['metamask_message'] = generated_message

    return Response(generated_message)


@api_view(http_method_names=['GET'])
def plan_price(request):
    """Plan price"""
    price = PlanPrice.objects.all().first()
    return Response(price.price)


@swagger_auto_schema(
    method='get',
    operation_description="Get favourite pairs of the current user for the specified platform",
    manual_parameters=[
        openapi.Parameter(name='platform',
                          required=True,
                          in_='path',
                          description='Platform name (e.g. "ETH")',
                          type='string',
                          enum=['ETH', 'BSC', 'POLYGON'])
    ],
    responses={'200': serializers.ListSerializer(child=serializers.CharField(max_length=50)),
               '403': 'Invalid authentication (no such user in the DB)',
               '406': 'Unsupported user type for this operation'}
)
@api_view(http_method_names=['GET'])
@permission_classes([IsAuthenticated])
def get_favourite_pairs(request, platform='ETH'):
    try:
        username = Web3.toChecksumAddress(request.user.username)
    # if it's a user without hex-string username (e.g. admins)
    except ValueError:
        print(f'unsupported type of user is retrieving favourite pairs ({request.user} in this case)')
        return Response('Unsupported user type for this operation', status=status.HTTP_406_NOT_ACCEPTABLE)

    user_filter = AdvUser.objects.filter(username__iexact=username)
    if not user_filter.exists():
        return Response(f'No user {username} record in the database', status=status.HTTP_403_FORBIDDEN)

    user = user_filter.first()
    platform = platform.upper()

    favourite_pairs = []
    for pair in user.favourite_pairs.filter(platform=platform).all():
        favourite_pairs.append(pair.address)

    return Response(favourite_pairs, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Add/remove pair to/from favourites.\n"
                          "If the specified pair is already favourite, it will be removed from favourites.\n"
                          "Returns True if pair is added to favourites, False - if removed",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'pair_address': openapi.Schema(type=openapi.TYPE_STRING),
            'platform': openapi.Schema(type=openapi.TYPE_STRING, enum=['ETH', 'BSC', 'POLYGON']),
        },
        required=['pair_address', 'platform']
    ),
    responses={'200': 'True if pair is now favourite, False otherwise',
               '207': 'Favourite pairs count limit exceeded for the user',
               '403': 'Invalid authentication (no such user in the DB)',
               '404': 'No such pair in the DB',
               '406': 'Unsupported user type for this operation'}
)
@api_view(http_method_names=['POST'])
@permission_classes([IsAuthenticated])
def add_or_remove_favourite_pair(request):
    try:
        username = Web3.toChecksumAddress(request.user.username)
    # if it's a user without hex-string username (e.g. admins)
    except ValueError:
        print(f'unsupported type of user is trying to add/remove favourite pairs ({request.user} in this case)')
        return Response('Unsupported user type for this operation', status=status.HTTP_406_NOT_ACCEPTABLE)

    user_filter = AdvUser.objects.filter(username__iexact=username)
    if not user_filter.exists():
        return Response(f'No user {username} record in the database', status=status.HTTP_403_FORBIDDEN)

    user = user_filter.first()

    pair_address = Web3.toChecksumAddress(request.data['pair_address'])
    platform = request.data['platform'].upper()

    pair_filter = Pair.objects.filter(address=pair_address, platform=platform)
    if not pair_filter.exists():
        return Response(f'No pair {pair_address} record in the database', status=status.HTTP_404_NOT_FOUND)

    pair = pair_filter.first()
    if user.favourite_pairs.filter(address=pair_address, platform=platform).exists():
        user.favourite_pairs.remove(pair)
        return Response(False, status=status.HTTP_200_OK)
    if user.plan == AdvUser.Plans.FREE and user.favourite_pairs.all().count() < FAVOURITE_PAIRS_LIMIT:
        user.favourite_pairs.add(pair)
        return Response(True, status=status.HTTP_200_OK)
    else:
        return Response(f'Favourite pairs count limit exceeded for the user. Current plan: {user.plan}.'
                        f' Limit of {FAVOURITE_PAIRS_LIMIT} for user {user.username} is reached',
                        status=status.HTTP_207_MULTI_STATUS)

