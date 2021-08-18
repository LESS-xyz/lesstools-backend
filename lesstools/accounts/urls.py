from django.urls import path
from lesstools.accounts.views import MetamaskLogin, UserApiView
from lesstools.accounts.api import generate_metamask_message, plan_price, get_favourite_pairs, \
    add_or_remove_favourite_pair

urlpatterns = [
    path('metamask_login/', MetamaskLogin.as_view(), name='metamask_login'),
    path('get_metamask_message/', generate_metamask_message),
    path('', UserApiView.as_view()),
    path('price/', plan_price),
    path('favourite_pairs/<str:platform>', get_favourite_pairs),
    path('add_or_remove_favourite_pair/', add_or_remove_favourite_pair),
]
