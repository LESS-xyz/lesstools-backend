from django.urls import path
from lesstools.analytics.views import pair_info_retrieval, manual_cmc_mapping_update, pair_vote, Candles

urlpatterns = [
    path('pair_info', pair_info_retrieval, name='Pair Explorer'),
    path('manual_cmc_mapping_update', manual_cmc_mapping_update, name='Manual update of CoinMarketCap IDs map'),
    path('pair_vote', pair_vote, name='Vote for pair (like/dislike)'),
    path('candles/<str:pair_id>&<str:pool>&<str:time_interval>&<int:candles>', Candles.as_view(), name='Create candles')
    path('candles/<str:pair_id>&<str:pool>&<str:time_interval>', Candles.as_view(), name='Create candles')
]
