import json
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
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
            streamers = Streamer.objects.filter(isAtHome=True, isActive=True).order_by('?')[:10]
        else:
            streamers = Streamer.objects.filter(isActive=True).order_by('orderPP')
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


class DeleteItem(APIView):
    def post(self, request):
        session_id = request.data.get('session_id')
        item_id = request.data.get('item_id')
        ticket = CartItem.objects.get(id=item_id)
        ticket.delete()
        calculate_cart_price(cart=check_if_cart_exists(session_id))
        return Response(status=200)


class AddItemQuantity(APIView):
    def post(self, request):
        session_id = request.data.get('session_id')
        item_id = request.data.get('item_id')
        ticket = CartItem.objects.get(id=item_id)
        ticket.quantity +=1
        ticket.save()
        calculate_cart_price(cart = check_if_cart_exists(session_id))
        return Response(status=200)


class DeleteItemQuantity(APIView):
    def post(self, request):
        session_id = request.data.get('session_id')
        item_id = request.data.get('item_id')
        ticket = CartItem.objects.get(id=item_id)
        if ticket.quantity > 1:
            ticket.quantity -= 1
            ticket.save()
        else:
            ticket.delete()
        calculate_cart_price(cart = check_if_cart_exists(session_id))
        return Response(status=200)


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
            calculate_cart_price(cart)
        except CartItem.DoesNotExist:
            item = CartItem.objects.create(
                t_id=f'{session_id}-{item_id}-{streamer_id}',
                ticket_id=item_id,
                streamer_id=streamer_id if streamer_id != 0 else None
            )
            cart.tickets.add(item)
            calculate_cart_price(cart)

        return Response(status=200)


class CreateOrder(APIView):
    def post(self,request):
        print(request.data)
        session_id = request.data.get('session_id')
        cart = check_if_cart_exists(session_id)
        new_order = Order.objects.create(
            name=request.data.get('name'),
            family=request.data.get('family'),
            email=request.data.get('email'),
            phone=request.data.get('phone')
        )
        cart_items = cart.tickets.all()
        for i in cart_items:
            new_item = OrderItem.objects.create(
                o_id=new_order.u_id,
                ticket=i.ticket,
                streamer=i.streamer,
                quantity=i.quantity
            )
            new_order.tickets.add(new_item)
        clear_cart(cart)
        serializer = OrderSerializer(new_order)
        return Response(serializer.data, status=200)


class GetTicket(generics.RetrieveAPIView):
    serializer_class = OrderItemSerializer

    def get_object(self):
        return OrderItem.objects.get(u_id=self.request.query_params.get('uuid'))


class SubscribeEmail(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            validate_email(email)
            try:
                subscribe_model_instance = Subscribe.objects.get(email=email)
            except Subscribe.DoesNotExist as e:
                subscribe_model_instance = Subscribe()
                subscribe_model_instance.email = email
            subscribe_model_instance.save()
            return Response(status=200)
        except ValidationError:
            return Response(status=400)
