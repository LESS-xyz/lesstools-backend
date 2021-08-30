from rest_framework import serializers
from . import models


class UserSerializer(serializers.ModelSerializer):
    paid_until = serializers.SerializerMethodField()
    holdings = serializers.SerializerMethodField()

    class Meta:
        model = models.AdvUser
        read_only_field = ('paid_until', 'holdings',)
        fields = read_only_field + ('id', 'username', 'plan_by_payments', 'plan_by_holding')

    def get_paid_until(self, obj):
        return obj.payments.order_by('-end_time').first().end_time \
               if obj.payments.order_by('-end_time').first() else None

    def get_holdings(self, obj):
        return {holding.network.name: holding.less_holding_amount
                for holding in obj.holds.filter(network__allows_holding_for_paid_plans=True)}


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PlanPrice
        read_only_field = ('monthly_price_in_usd', 'holding_amount_in_less',)
        fields = read_only_field
