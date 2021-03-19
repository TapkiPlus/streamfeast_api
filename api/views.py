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


class GetStreamerStats(generics.RetrieveAPIView):
    serializer_class = StreamerSerializer

    def get_object(self):
        print(self.request.query_params.get('uniqUrl'))
        return Streamer.objects.get(uniqUrl=self.request.query_params.get('uniqUrl'))


 
class GetFaq(generics.ListAPIView):
    serializer_class = FaqSerializer
    queryset = Faq.objects.all()


class GetHowTo(generics.ListAPIView):
    serializer_class = HowToSerializer
    queryset = HowTo.objects.all()


class GetTicketTypes(generics.ListAPIView):
    serializer_class = TicketTypeSerializer
    queryset = TicketType.objects.all()


class GetCart(generics.RetrieveAPIView):
    serializer_class = CartSerializer

    def get_object(self):
        session_id = self.request.query_params.get('session_id')
        result = check_if_cart_exists(session_id)
        print("Result:")
        print(result)
        return result


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
        ticket_type_id = request.data.get('item_id')
        ticket_type = TicketType.objects.get(id = ticket_type_id)
        streamer_id = request.data.get('streamer_id')
        streamer = None
        if streamer_id != 0:
            streamer = Streamer.objects.get(id = streamer_id)
        cart = check_if_cart_exists(session_id)

        print("Cart:")
        print(cart)

        item, created = CartItem.objects.get_or_create(parent = cart, ticket_type = ticket_type, streamer = streamer)
        item.quantity += 1
        item.save()
        calculate_cart_price(cart)
        cart.save()
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
        cart_items = CartItem.objects.filter(parent = cart)
        for i in cart_items:
            new_item = OrderItem.objects.create(
                order=new_order,
                ticket=i.ticket,
                quantity=i.quantity,
                streamer=i.streamer
            )
        clear_cart(cart)
        tx = platron_client.init_payment(new_order)
        return Response(tx.redirect_url, status = 200)


class GetTicketType(generics.RetrieveAPIView):
    serializer_class = OrderItemSerializer


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


class PaymentCheck(APIView):
    def post(self, request):
        xml = platron_client.payment_check(request.data)
        return Response(data = xml, status = 200, content_type = "text/xml")


class PaymentResult(APIView):
    def post(self, request):
        platron_client.payment_result(request.data)
        return Response(status = 200)


class TicketAsPdf(APIView):
    def get(self, request):
        ticket = Ticket.objects.first()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="ticket.pdf"'
        return response


class TicketClear(APIView):
    def get(self, request):
        id = request.query_params.ticket_id
        ticket = Ticket.objects.get(ticket_id = request.param.ticket_id)
        ticket.when_cleared = datetime.datetime.now()
        ticket.save()
        return Response(status = 200)

