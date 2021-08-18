from rest_framework import serializers
from . import models


class UserSerializer(serializers.ModelSerializer):
    paid_until = serializers.SerializerMethodField()

    class Meta:
        model = models.AdvUser
        read_only_field = ('paid_until',)
        fields = read_only_field + ('id', 'username', 'plan')

    def get_paid_until(self, obj):
        return obj.payments.order_by('-end_time').first().end_time \
               if obj.payments.order_by('-end_time').first() else None


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PlanPrice
        read_only_field = ('price',)
