import json

from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpResponse
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime
from dateutil import parser

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


class GetTicketTypes(generics.ListAPIView):
    serializer_class = TicketTypeSerializer
    queryset = TicketType.objects.all()


class GetCart(generics.RetrieveAPIView):
    serializer_class = CartSerializer

    def get_object(self):
        session_id = self.request.query_params.get('session_id')
        result, _ = Cart.objects.get_or_create(session=session_id)
        return result

class DeleteItem(APIView):
    def post(self, request):
        session_id = request.data.get('session_id')
        item_id = request.data.get('item_id')
        item = CartItem.objects.get(id=item_id)
        item.delete()
        cart, _ = Cart.objects.get_or_create(session=session_id)
        cart.calculate_cart_price()
        return Response(CartSerializer(cart).data)

class AddItemQuantity(APIView):
    def post(self, request):
        session_id = request.data.get('session_id')
        item_id = request.data.get('item_id')
        item = CartItem.objects.get(id=item_id)
        item.quantity += 1
        item.save()
        cart, _ = Cart.objects.get_or_create(session=session_id)
        cart.calculate_cart_price()
        return Response(CartSerializer(cart).data)

class DeleteItemQuantity(APIView):
    def post(self, request):
        session_id = request.data.get('session_id')
        item_id = request.data.get('item_id')
        item = CartItem.objects.get(id=item_id)
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()
        cart, _ = Cart.objects.get_or_create(session=session_id)
        cart.calculate_cart_price()
        return Response(CartSerializer(cart).data)


class AddItem(APIView):
    def post(self, request):
        session_id = request.data.get('session_id')
        ticket_type_id = request.data.get('item_id')
        ticket_type = TicketType.objects.get(id=ticket_type_id)
        streamer_id = request.data.get('streamer_id')
        streamer = None
        if streamer_id != 0:
            streamer = Streamer.objects.get(id=streamer_id)
        cart, _ = Cart.objects.get_or_create(session=session_id)
        item, _ = CartItem.objects.get_or_create(parent=cart, ticket_type=ticket_type, streamer=streamer)
        item.quantity += 1
        item.save()
        cart.calculate_cart_price()
        cart.save()
        return Response(CartSerializer(cart).data)

class SaveUserData(APIView):
    def post(self, request):
        from django.db.models import F
        session_id = request.data.get('session_id')
        allowed = ["firstname", "lastname", "email", "phone"] 
        update = {k: v for k, v in request.data.items() if k in allowed}
        if update:
            UserData.objects.update_or_create(session=session_id, defaults=update)

        increments = ["returnedToShop", "clickedPay", "tryedToPayAgain", "clickedTechAssistance"]
        inc_fields = {}
        for k, _ in request.data.items():
            if k in increments:
                inc_fields[k] = F[k] + 1
        if inc_fields:             
            UserData.objects.filter(session=session_id).update(inc_fields)
        
        return Response(status=200)


class GetUserData(generics.RetrieveAPIView):
    serializer_class = UserDataSerializer

    def get_object(self):
        ud, _ = UserData.objects.get_or_create(session=self.request.query_params.get('session_id'))
        return ud


class GetQr(APIView):
    def get(self, request):
        uuid = self.request.query_params.get('ticket_uuid')
        if Ticket.objects.filter(ticket_uuid=uuid).exists():
            response = HttpResponse(content=qr_code(uuid), content_type="image/png")
            return response
        else: 
            return Response(status=404)


class CreateOrder(APIView):

    def post(self, request):
        session_id = request.data['session_id']
        UserData.checkout(session_id)
        order = Order.create(session_id, request.data)
        tx = init_payment(order)
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


class TicketClear(APIView):
    def get(self, request):
        id = request.query_params.ticket_uuid
        ticket = Ticket.objects.get(ticket_uuid=request.param.ticket_uuid)
        ticket.when_cleared = datetime.now()
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


class GetStreamerStats(APIView): 

    def post(self, request):
        uid = request.data.get("streamer_uuid")
        start = None
        end = None
        if request.data.get("from"):
            start = parser.parse(request.data["from"])
        if request.data.get("till"):
            end = parser.parse(request.data["till"])

        streamer = Streamer.objects.get(uniqUrl=uid)
        summary = OrderItem.summary_by_uid(uid, start, end)
        items = OrderItem.items_by_uid(uid, start, end)
        
        stats = {
            "streamer": {
                "name": streamer.name,
                "nickName": streamer.nickName,
                "photo": streamer.photo.url
            },
            "summary": list(summary),
            "items": list(items)
        }

        return Response(json.dumps(stats, cls=DjangoJSONEncoder), content_type="application/json; charset=utf-8")


class GetStreamerOrders(generics.ListAPIView): 
    serializer_class = ActivitySerializer
    def get(self, request):
        uid = request.data["streamer_uuid"]
        queryset = OrderItem.objects.filter( \
            order__when_paid__isnull=False, \
            streamer__uniqUrl=uid \
        )

class GetStreamerOrdersTotals(APIView): 
    def get(self, request):
        uid = request.data["streamer_uuid"]
