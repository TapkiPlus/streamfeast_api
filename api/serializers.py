from rest_framework import serializers
from .models import *


class FaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        fields = '__all__'


class HowToSerializer(serializers.ModelSerializer):
    class Meta:
        model = HowTo
        fields = '__all__'


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'


class StreamerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Streamer
        fields = '__all__'


class CartItemSerializer(serializers.ModelSerializer):
    streamer = StreamerSerializer(many=False, read_only=True, required=False)

    class Meta:
        model = CartItem
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True, required=False)

    class Meta:
        model = Cart
        fields = '__all__'



