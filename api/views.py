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


class GetFaq(generics.ListAPIView):
    serializer_class = FaqSerializer
    queryset = Faq.objects.all()


class GetHowTo(generics.ListAPIView):
    serializer_class = HowToSerializer
    queryset = HowTo.objects.all()


class GetTickets(generics.ListAPIView):
    serializer_class = TicketSerializer
    queryset = Ticket.objects.all()


class GetCart(generics.RetrieveAPIView):
    serializer_class = TicketSerializer

    def get_object(self):
        session_id = self.request.query_params.get('session_id')
        return check_if_cart_exists(session_id)