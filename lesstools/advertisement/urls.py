from django.urls import path
from .views import img_urls


urlpatterns = [
    path('img_urls/', img_urls),
]
