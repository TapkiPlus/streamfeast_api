from rest_framework import serializers

from .models import *


class FaqCommonSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaqCommon
        fields = '__all__'

class FaqParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaqParticipant
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

class FastStreamerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Streamer
        fields = ['id', 'nickName', 'nickNameSlug', 'photo', 'email', 'isActive']


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

    class Meta:
        model = Ticket
        fields = '__all__'


class PlaceTimetableSerializer(serializers.ModelSerializer):
    streamers = FastStreamerSerializer(many=True, required=True)

    class Meta:
        model = PlaceTimetable
        fields = '__all__'
        extra_fields = ['streamers']

class PlaceSerializer(serializers.ModelSerializer):
    timetable = PlaceTimetableSerializer(many=True, required=True)
    class Meta:
        model = Place
        fields = ['id', 'number', 'name', 'level', 'timetable']


class ActivitySerializer(serializers.ModelSerializer):
    place = PlaceSerializer(many=False)
    streamers = StreamerSerializer(many=True, required=True)

    class Meta:
        model = Activity
        fields = '__all__'
        extra_fields = ['streamers']
