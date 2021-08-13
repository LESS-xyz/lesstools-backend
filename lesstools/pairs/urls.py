from django.urls import path
from .views import like, dislike

urlpatterns = [
    path('like/<int:pk>/', like),
    path('dislike/<int:pk>/', dislike),
]
