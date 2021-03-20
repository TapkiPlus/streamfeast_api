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


class ChangeItemQuantity(APIView):
    def post(self, request):
        session_id = request.data.get('session_id')
        item_id = request.data.get('item_id')
        ticket = CartItem.objects.get(id=item_id)
        ticket.quantity = request.data.get('quantity')
        ticket.save()
        calculate_cart_price(cart = check_if_cart_exists(session_id))
        return Response(status=200)

# class AddItemQuantity(APIView):
#     def post(self, request):
#         session_id = request.data.get('session_id')
#         item_id = request.data.get('item_id')
#         ticket = CartItem.objects.get(id=item_id)
#         ticket.quantity +=1
#         ticket.save()
#         calculate_cart_price(cart = check_if_cart_exists(session_id))
#         return Response(status=200)


# class DeleteItemQuantity(APIView):
#     def post(self, request):
#         session_id = request.data.get('session_id')
#         item_id = request.data.get('item_id')
#         ticket = CartItem.objects.get(id=item_id)
#         if ticket.quantity > 1:
#             ticket.quantity -= 1
#             ticket.save()
#         else:
#             ticket.delete()
#         calculate_cart_price(cart = check_if_cart_exists(session_id))
#         return Response(status=200)


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


class SaveUserData(APIView):
    def post(self,request):
     session_id = request.data.get('session_id')
     firstname= request.data.get('firstname')
     lastname= request.data.get('lastname')
     email= request.data.get('email')
     phone= request.data.get('phone')
     wentToCheckout= request.data.get('wentToCheckout')
     returnedToShop= request.data.get('returnedToShop')
     leftCheckout = request.data.get('leftCheckout')
     returnedToCart = request.data.get('returnedToCart')
     clickedPay = request.data.get('clickedPay')
     payed= request.data.get('payed')
     notPayed= request.data.get('notPayed')
     tryedToPayAgain= request.data.get('tryedToPayAgain')
     closedFailPage=  request.data.get('closedFailPage')
     clickedTechAssistance = request.data.get('clickedTechAssistance')
     try:
        userData = UserData.objects.get(session=session_id)
        if firstname:
            userData.firstname = firstname
        elif lastname:
            userData.lastname = lastname
        elif email:
            userData.email = email
        elif phone:
            userData.phone = phone
        elif wentToCheckout:
            userData.wentToCheckout += 1
        elif returnedToShop:
            userData.returnedToShop += 1
        elif leftCheckout:
            userData.leftCheckout += 1 
        elif returnedToCart:
            userData.returnedToCart += 1
        elif clickedPay:
            userData.clickedPay += 1
        elif payed:
            userData.payed += 1
        elif notPayed:
            userData.notPayed += 1
        elif tryedToPayAgain:
            userData.tryedToPayAgain += 1
        elif closedFailPage:
            userData.closedFailPage += 1
        elif clickedTechAssistance:
            userData.clickedTechAssistance += 1 
        userData.save()
     except UserData.DoesNotExist:
       UserData.objects.create(
            session=session_id,
            firstname=firstname if firstname else '',
            lastname=lastname if lastname else '',
            email=email if email else '',
            phone=phone if phone else '',
            wentToCheckout=wentToCheckout if 1 else 0,
            returnedToShop=returnedToShop if 1 else 0,
            leftCheckout=leftCheckout if 1 else 0,
            returnedToCart=returnedToCart if 1 else 0,
            clickedPay=clickedPay if 1 else 0,
            payed=payed if 1 else 0,
            notPayed=notPayed if 1 else 0,
            tryedToPayAgain=tryedToPayAgain if 1 else 0,
            closedFailPage=closedFailPage if 1 else 0,
            clickedTechAssistance=clickedTechAssistance if 1 else 0,
        ).save()
     return Response(status=200)

class GetUserData(generics.RetrieveAPIView):
    serializer_class = UserDataSerializer
    def get_object(self):
        return UserData.objects.get(session=self.request.query_params.get('session_id'))


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
