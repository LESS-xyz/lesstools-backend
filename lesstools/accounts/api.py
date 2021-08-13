from random import choice
from string import ascii_letters

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from eth_utils.hexadecimal import add_0x_prefix
from eth_account.messages import encode_defunct
from eth_account import Account

from lesstools.accounts.models import PlanPrice

import logging


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
