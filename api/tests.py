from django.test import TestCase
from django.test import Client
from api import modul_client

from .models import *
from .email_client import send_application
from django.test.utils import override_settings
from datetime import datetime

__sample_txn = {
    "testing": "1",
    "pan_mask": "220011******4440",
    "unix_timestamp": "1570161434",
    "salt": "DB9481A6554924BFD2F2279B5AD05B9D",
    "rrn": "927703219385",
    "transaction_id": "0EyuFLLZ9DagCXy8O67Q6x",
    "original_amount": "10.00",
    "auth_number": "2164219385",
    "amount": "10.00",
    "created_datetime": "2019-10-04 03:56:09",
    "auth_code": "201471",
    "signature": "622e1486dba17d05d080c6734131205a75d59188",
    "client_phone": "+79999999999",
    "client_email": "example@example.ru",
    "state": "COMPLETE",
    "order_id": "77777-01",
    "currency": "RUB",
    "merchant": "51cb8a0f-6fb8-4a20-98b1-9fd85dc47500",
    "payment_method": "card",
    "meta": "{'bill_id': 'vlICmFjY7nST9KARa5RsSJ'}"
}

# Modulbank testing suite
class ModuleTestCase(TestCase): 
    def setUp(self): 
        data = UserData.objects.create(session="123")
        streamer = Streamer.objects.create(name="Vasya")
        order = Order.objects.create(id="77777-01", amount=128, email="dzenmassta@gmail.com", created_at=datetime.utcnow())
        OrderItem.objects.create(order=order, ticket_type=1, quantity=1, amount=42, price=42, streamer=streamer)
        OrderItem.objects.create(order=order, ticket_type=2, quantity=2, amount=86, price=43)

        
    #@override_settings(PAYMENT_KEY='2618109CC214F9AFE0F855AE582A9BC4')
    #@override_settings(PAYMENT_MERCHANT_ID='c2659e97-cf26-421e-8a2e-91973e9bb5c2')
    def test_make_payment(self): 
        resp=modul_client.make_purchase("77777-01")
        print(f"Resp: {resp}")

    def test_complete_payment(self):
        cli = Client()
        response = cli.post("/api/payment_result", __sample_txn)
        print("Response status: " + str(response.status_code))
        assert response.status_code == 200

        paid_order = Order.objects.get(id="77777-01")
        for key, value in paid_order.__dict__.items(): 
            print(key + " -> " + str(value))
        assert paid_order.when_paid


class TicketTestCase(TestCase):

    def setUp(self):
        data = UserData.objects.create(session="123")
        streamer = Streamer.objects.create(name="Vasya")
        order = Order.objects.create(id="77777-01", amount=128, email="dzenmassta@gmail.com", created_at=datetime.utcnow())
        OrderItem.objects.create(order=order, ticket_type=1, quantity=1, amount=42, price=42, streamer=streamer)
        OrderItem.objects.create(order=order, ticket_type=2, quantity=2, amount=86, price=43)
        # set paid
        txn = ModulTxnForm(__sample_txn).save()
        Order.set_paid_by(txn)
        pass

    def test_sent(self): 
        queryset = Order.objects.filter(id="77777-01")
        Ticket.objects.filter(order__in=queryset).update(when_sent=None, send_attempts=5)
        all_tickets = Ticket.objects.all()
        for ticket in all_tickets: 
            print("Ticket: {}, {}, {}".format(ticket.ticket_id, ticket.when_sent, ticket.send_attempts))

    def test_user_data(self): 
        increments = ["returnedToShop", "clickedPay", "tryedToPayAgain", "clickedTechAssistance"]
        inc_fields = {}
        for k in increments:
            inc_fields[k] = F(k) + 5
        if inc_fields:             
            UserData.objects.filter(session="123").update(**inc_fields)
        data = UserData.objects.get(session="123")
        print("Data: {} {} {} {}".format(data.returnedToShop, data.clickedPay, data.tryedToPayAgain, data.clickedTechAssistance))

        
    def test_select_uuid(self): 
        ticket = Ticket.objects.first()
        print("uuid: {}".format(ticket.ticket_uuid))
        t2 = Ticket.objects.filter(ticket_uuid=ticket.ticket_uuid).first()
        t2.ticket_uuid = "2399457e-7ab6-406f-b68f-d4a21e0171ae"
        t2.save()
        print("t2: {}".format(t2))
        t3 = Ticket.objects.filter(ticket_uuid="2399457e-7ab6-406f-b68f-d4a21e0171ae").first()
        print("t3: {}".format(t3))
        



    #to test SMTP uncomment this pls
    #@override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
    def test_order_paid(self):
        pass
        # order = Order.objects.last()
        # send_application(order)
        # tickets = Ticket.objects.all()
        # for t in tickets:
        #     file = t.pdf(filename=f'{t.ticket_id}.pdf')
        #     print("FFF")
        #     print(file)

    def test_summary(self):
        streamer = Streamer.objects.get(name="Vasya")
        result = OrderItem.summary_by_uid(streamer.uniqUrl, end = datetime.utcnow())
        print("Summary: {}".format(result))

    def test_stats(self):
        streamer = Streamer.objects.get(name="Vasya")
        result = OrderItem.items_by_uid(streamer.uniqUrl, end = datetime.utcnow())
        print("Stats: {}".format(result))

    def test_summary_stats(self): 
        import json
        from django.core.serializers.json import DjangoJSONEncoder
        streamer = Streamer.objects.get(name="Vasya")
        summary = OrderItem.summary_by_uid(streamer.uniqUrl, None, None)
        items = OrderItem.items_by_uid(streamer.uniqUrl, None, None)
        stats = {
            "streamer": {
                "name": streamer.name,
                "nickName": streamer.nickName,
                "photo": "photo url"
            },
            "summary": list(summary),
            "items": list(items)
        }
        print("Json: {}".format(json.dumps(stats, cls=DjangoJSONEncoder)))
