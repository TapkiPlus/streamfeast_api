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


class StreamerSerializer(serializers.ModelSerializer):
    links = SocialLinkSerializer(many=True, read_only=True, required=False)

    class Meta:
        model = Streamer
        fields = '__all__'

    def to_representation(self, instance):
        response = super(StreamerSerializer, self).to_representation(instance)
        if instance.photo:
            response['photo'] = instance.photo.url
        if instance.pageHeader:
            response['pageHeader'] = instance.pageHeader.url
        return response


class CartItemSerializer(serializers.ModelSerializer):
    ticket = TicketSerializer(many=False, read_only=True, required=False)
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
    ticket = TicketSerializer(many=False, read_only=True, required=False)
    streamer = StreamerSerializer(many=False, read_only=True, required=False)
    is_payed = serializers.SerializerMethodField()
    order_name = serializers.SerializerMethodField()
    order_family = serializers.SerializerMethodField()
    order_email = serializers.SerializerMethodField()
    order_phone = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = '__all__'

    def get_is_payed(self, obj):
        order = Order.objects.get(u_id=obj.o_id)
        return order.is_payed

    def get_order_name(self, obj):
        order = Order.objects.get(u_id=obj.o_id)
        return order.name

    def get_order_family(self, obj):
        order = Order.objects.get(u_id=obj.o_id)
        return order.family

    def get_order_email(self, obj):
        order = Order.objects.get(u_id=obj.o_id)
        return order.email

    def get_order_phone(self, obj):
        order = Order.objects.get(u_id=obj.o_id)
        return order.phone


class OrderSerializer(serializers.ModelSerializer):
    tickets = OrderItemSerializer(many=True, read_only=True, required=False)

    class Meta:
        model = Order
        fields = '__all__'


class PlaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Place
        fields = '__all__'


class ActivitySerializer(serializers.ModelSerializer):
    place = PlaceSerializer(many=False, required=True)
    streamer = StreamerSerializer(many=False, required=True)

    class Meta:
        model = Activity
        fields = '__all__'
