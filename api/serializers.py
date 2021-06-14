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

    def to_representation(self, instance):
        response = super(SocialIconSerializer, self).to_representation(instance)
        if instance.icon:
            response['icon'] = instance.icon.url
        return response


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

    class Meta:
        model = Streamer
        exclude = ['uniqUrl']

    def to_representation(self, instance):
        response = super(StreamerSerializer, self).to_representation(instance)
        if instance.photo:
            response['photo'] = instance.photo.url
        if instance.pageHeader:
            response['pageHeader'] = instance.pageHeader.url
        return response


class CartItemSerializer(serializers.ModelSerializer):
    ticket_type = TicketTypeSerializer(many=False, read_only=True, required=False)
    streamer = StreamerSerializer(many=False, read_only=True, required=False)

    class Meta:
        model = CartItem
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    cartitem_set = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = '__all__'


class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
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
        return OrderItem.objects.get(order=obj)

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
        model = Ticket
        fields = '__all__'


class PlaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Place
        fields = '__all__'


class ActivitySerializer(serializers.ModelSerializer):
    place = PlaceSerializer(many=False)
    streamers = StreamerSerializer(many=True, required=True)

    class Meta:
        model = Activity
        fields = '__all__'
        extra_fields = ['streamers']
