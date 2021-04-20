from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpResponse
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from .platron_client import *
from .serializers import *
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
        ticket.quantity += 1
        ticket.save()
        calculate_cart_price(cart=check_if_cart_exists(session_id))
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
        calculate_cart_price(cart=check_if_cart_exists(session_id))
        return Response(status=200)


class AddItem(APIView):
    def post(self, request):
        print(request.data)
        session_id = request.data.get('session_id')
        ticket_type_id = request.data.get('item_id')
        ticket_type = TicketType.objects.get(id=ticket_type_id)
        streamer_id = request.data.get('streamer_id')
        streamer = None
        if streamer_id != 0:
            streamer = Streamer.objects.get(id=streamer_id)
        cart = check_if_cart_exists(session_id)

        item, created = CartItem.objects.get_or_create(parent=cart, ticket_type=ticket_type, streamer=streamer)
        item.quantity += 1
        item.save()
        calculate_cart_price(cart)
        cart.save()
        return Response(status=200)


class SaveUserData(APIView):
    def post(self, request):
        session_id = request.data.get('session_id')
        user_data = UserData.objects.get_or_create(session=session_id)
        user_data.firstname = request.data.get('firstname')
        user_data.lastname = request.data.get('lastname')
        user_data.email = request.data.get('email')
        user_data.phone = request.data.get('phone')

        if request.data.get('wentToCheckout'):
            user_data.wentToCheckout += 1
        if request.data.get('returnedToShop'):
            user_data.returnedToShop += 1
        if request.data.get('clickedPay'):
            user_data.clickedPay += 1
        if request.data.get('tryedToPayAgain'):
            user_data.tryedToPayAgain += 1
        if request.data.get('clickedTechAssistance'):
            user_data.clickedTechAssistance += 1

        user_data.save()

        return Response(status=200)


class GetUserData(generics.RetrieveAPIView):
    serializer_class = UserDataSerializer

    def get_object(self):
        return UserData.objects.get_or_create(session=self.request.query_params.get('session_id'))


class CreateOrder(APIView):

    @transaction.atomic
    def post(self, request):
        print(request.data)
        session_id = request.data.get('session_id')
        cart = check_if_cart_exists(session_id)
        user_data = UserData.objects.get_or_create(session=session_id)
        order_id = '{:05d}-{:02d}'.format(user_data.id, user_data.wentToCheckout)
        new_order = Order.objects.create(
            id=order_id,
            name=request.data.get('name'),
            family=request.data.get('family'),
            email=request.data.get('email'),
            phone=request.data.get('phone')
        )
        cart_items = CartItem.objects.filter(parent=cart)
        index = 0
        for i in cart_items:
            index += 1
            new_item = OrderItem.objects.create(
                item_id='{}-{:02d}'.format(new_order.id, index),
                order=new_order,
                ticket_type=i.ticket_type,
                quantity=i.quantity,
                streamer=i.streamer,
                amount=i.quantity * i.ticket_type.price
            )
            new_order.amount += new_item.amount
        clear_cart(cart)
        tx = init_payment(new_order)
        tx.save()
        return Response(tx.redirect_url, status=200)


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
        xml = payment_check(request.data)
        return HttpResponse(content=xml, status=200, content_type="application/xml")


class PaymentResult(APIView):
    def post(self, request):
        xml = payment_result(request.data)
        return HttpResponse(content=xml, status=200, content_type="application/xml")


class TicketAsPdf(APIView):
    def get(self, request):
        ticket = Ticket.objects.first()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="ticket.pdf"'
        return response


class TicketClear(APIView):
    def get(self, request):
        id = request.query_params.ticket_uuid
        ticket = Ticket.objects.get(ticket_uuid=request.param.ticket_uuid)
        ticket.when_cleared = datetime.datetime.now()
        ticket.save()
        return Response(status=200)

      
class GetActivities(generics.ListAPIView):
    serializer_class = ActivitySerializer
    queryset = Activity.objects.all()


class GetActivity(generics.RetrieveAPIView):
    serializer_class = ActivitySerializer

    def get_object(self):
        activity_id = self.request.query_params.get('activity_id')
        return Activity.objects.get(id=activity_id)

