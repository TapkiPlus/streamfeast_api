import json
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from .serializers import *
from .models import *
from .services import *


class GetStreamer(generics.RetrieveAPIView):
    serializer_class = StreamerSerializer

    def get_object(self):
        return Streamer.objects.get(nickNameSlug=self.request.query_params.get('name_slug'))


class GetStreamers(generics.ListAPIView):
    serializer_class = StreamerSerializer

    def get_queryset(self):
        print()
        if self.request.query_params.get('at_home') == 'show':
            streamers = Streamer.objects.filter(isAtHome=True)
        else:
            streamers = Streamer.objects.all()
        return streamers

