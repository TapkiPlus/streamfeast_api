from rest_framework import serializers
from .models import *


class StreamerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Streamer
        fields = '__all__'


# class ItemTypeSerializer(serializers.ModelSerializer):
#     item = ItemSerializer(many=False, read_only=True, required=False)
#     color = ItemColorSerializer(many=False, read_only=True, required=False)
#     size = ItemSizeSerializer(many=False, read_only=True, required=False)
#     height = ItemHeightSerializer(many=False, read_only=True, required=False)
#
#     class Meta:
#         model = ItemType
#         fields = '__all__'


