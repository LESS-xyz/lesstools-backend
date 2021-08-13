from .models import Pairs
from rest_framework.exceptions import PermissionDenied


def like(request):
    """New like to pair"""
    if request.user.is_authenticated():
        pair = Pairs.objects.get(id=request.pk)
        return pair.like()
    else:
        raise PermissionDenied(1034)


def dislike(request):
    """New dislike to pair"""
    if request.user.is_authenticated():
        pair = Pairs.objects.get(id=request.pk)
        return pair.dislike()
    else:
        raise PermissionDenied(1034)
