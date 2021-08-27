from rest_framework import serializers
from .models import ADV


class ImgSerializer(serializers.ModelSerializer):
    icon_path = serializers.SerializerMethodField()
    icon_url = serializers.SerializerMethodField()

    class Meta:
        model = ADV
        fields = ('name', 'sub_name', 'icon_path', 'icon_url', 'description', 'position', 'hash')

    @staticmethod
    def get_icon_path(obj):
        return obj.icon.path

    @staticmethod
    def get_icon_url(obj):
        return obj.icon.url
