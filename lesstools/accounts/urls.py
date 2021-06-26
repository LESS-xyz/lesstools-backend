from django.urls import path
from lesstools.accounts.views import MetamaskLogin, UserApiView
from lesstools.accounts.api import generate_metamask_message

urlpatterns = [
    path('metamask_login/', MetamaskLogin.as_view(), name='metamask_login'),
    path('get_metamask_message/', generate_metamask_message),
    path('', UserApiView.as_view())
]