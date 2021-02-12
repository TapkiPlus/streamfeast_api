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
    serializer_class = CartSerializer

    def get_object(self):
        session_id = self.request.query_params.get('session_id')
        return check_if_cart_exists(session_id)

class AddItem(APIView):
    def post(self,request):
        print(request.data)
        session_id = request.data.get('session_id')
        item_id = request.data.get('item_id')
        streamer_id = request.data.get('streamer_id')
        cart = check_if_cart_exists(session_id)
        print(cart)

        try:
            ticket = CartItem.objects.get(t_id=f'{session_id}-{item_id}-{streamer_id}')
            ticket.quantity += 1
            ticket.save()
        except CartItem.DoesNotExist:
            item = CartItem.objects.create(t_id=f'{session_id}-{item_id}-{streamer_id}',
                                    ticket_id=item_id,
                                    streamer_id=streamer_id if streamer_id != 0 else None)
            cart.tickets.add(item)

        return Response(status=200)