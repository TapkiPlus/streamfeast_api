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


class TicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = '__all__' 


class SocialIconSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialIcon
        fields = '__all__'


class SocialLinkSerializer(serializers.ModelSerializer):
    icon = SocialIconSerializer(many=False, read_only=True, required=False)

    class Meta:
        model = SocialLink
        fields = '__all__'


class SoldTicketTypeSerializer(serializers.ModelSerializer):
    ticket = TicketTypeSerializer(many=False, read_only=True, required=False)

    class Meta:
        model = CartItem
        fields = '__all__'


class StreamerSerializer(serializers.ModelSerializer):
    links = SocialLinkSerializer(many=True, read_only=True, required=False)
    sold_tickets = SoldTicketTypeSerializer(many=True, read_only=True, required=False)
    sold_tickets_price = serializers.SerializerMethodField()

    class Meta:
        model = Streamer
        exclude = ['uniqUrl']

    def get_sold_tickets_price(self, obj):
        total_price = 0
        for i in obj.sold_tickets.all():
            total_price += i.ticket.price * i.quantity
        return total_price


class CartItemSerializer(serializers.ModelSerializer):
    ticket = TicketTypeSerializer(many=False, read_only=True, required=False)
    streamer = StreamerSerializer(many=False, read_only=True, required=False)

    class Meta:
        model = CartItem
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    tickets = CartItemSerializer(many=True, read_only=True, required=False)

    class Meta:
        model = Cart
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    ticket = TicketTypeSerializer(many=False, read_only=True, required=False)
    streamer = StreamerSerializer(many=False, read_only=True, required=False)

    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    def get_items(self, obj):
        return OrderItem.objects.get(order=order.id)

    class Meta:
        model = Order
        fields = '__all__'


class OrderShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class TicketSerializer(serializers.ModelSerializer):
    order = OrderShortSerializer(read_only=True)
    item = OrderItemSerializer(read_only=True)

    def get_item(self, obj):
        return OrderItem.objects.get(order=order.id)

    def get_order(self, obj):
        return OrderItem.objects.get(order=order.id)

    class Meta:
        model = Order
        fields = '__all__'
