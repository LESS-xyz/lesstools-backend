from django.urls import path
from lesstools.analytics.views import pair_info_retrieval, manual_cmc_mapping_update

urlpatterns = [
    path('pair_info', pair_info_retrieval, name='Pair Explorer'),
    path('manual_cmc_mapping_update', manual_cmc_mapping_update, name='Manual update of CoinMarketCap IDs map'),
]
