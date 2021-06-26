from .models import AdvUser
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_auth.registration.serializers import SocialLoginSerializer
from rest_framework.exceptions import PermissionDenied
from rest_auth.registration.views import SocialLoginView
from rest_framework import serializers
from lesstools.accounts.api import valid_metamask_message
from lesstools.accounts.serializers import UserSerializer




class MetamaskLoginSerializer(SocialLoginSerializer):
    address = serializers.CharField(required=False, allow_blank=True)
    msg = serializers.CharField(required=False, allow_blank=True)
    signed_msg = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        address = attrs['address']
        signature = attrs['signed_msg']
        session = self.context['request'].session
        #message = session.get('metamask_message')
        message = None

        if message is None:
            message = attrs['msg']

        print('metamask login, address', address, 'message', message, 'signature', signature, flush=True)
        #check if signature is correct
        if valid_metamask_message(address, message, signature):
            metamask_user = AdvUser.objects.filter(username__iexact=address).first()
            if metamask_user is None:
                self.user = AdvUser(username=address)
                self.user.save()
                self.user.generate_keys()
                self.user.set_password(None)
            else:
                self.user = metamask_user
            attrs['user'] = self.user
        else:
            raise PermissionDenied(1034)

        return attrs


class MetamaskLogin(SocialLoginView):
    serializer_class = MetamaskLoginSerializer

    def login(self):
        self.user = self.serializer.validated_data['user']
        return super().login()


class UserApiView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    queryset = AdvUser.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = self.request.user
        return obj

