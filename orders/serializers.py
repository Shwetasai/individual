from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'product', 'quantity', 'ordered_at','total_price','status']
        read_only_fields = ['id', 'user', 'ordered_at']