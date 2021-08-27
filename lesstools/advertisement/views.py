from rest_framework.decorators import api_view
from lesstools.advertisement.models import ADV
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .serializers import ImgSerializer


@swagger_auto_schema(
    method='get',
    operation_description="ADV img",
    responses={'200': ImgSerializer(),
               '404': 'No such img in the DB'}
)
@api_view(http_method_names=['GET'])
def img_urls(request):
    image_info = ADV.objects.all()
    top = {}
    mid = {}
    bot = {}

    for img in image_info:
        if img.position == 'TOP':
            top[img.name] = [{'image_path': img.icon.path,
                              'image_url': img.icon.url,
                              'image_hash': img.get_ipfs_img()}]
        elif img.position == 'MID':
            mid[img.name] = [{'image_path': img.icon.path,
                              'image_url': img.icon.url,
                              'image_sub_name': img.sub_name,
                              'image_description': img.description,
                              'image_hash': img.get_ipfs_img()}]
        elif img.position == 'BOT':
            bot[img.name] = [{'image_path': img.icon.path,
                              'image_url': img.icon.url,
                              'image_hash': img.get_ipfs_img()}]
    context = {'TOP': top, 'MID': mid, 'BOT': bot}

    return Response(context)
