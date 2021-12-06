from django.urls import path
from lesstools.analytics.views import pair_info_retrieval, manual_cmc_mapping_update, pair_vote, Candles, AdminTokens
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('pair_info', pair_info_retrieval, name='Pair Explorer'),
    path('manual_cmc_mapping_update', manual_cmc_mapping_update, name='Manual update of CoinMarketCap IDs map'),
    path('pair_vote', pair_vote, name='Vote for pair (like/dislike)'),
    path('candles/<str:pair_id>&<str:pool>&<str:time_interval>&<int:candles>', Candles.as_view(), name='Create candles'),
    path('admin_tokens/', AdminTokens.as_view(), name='Admin tokens'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
