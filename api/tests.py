from django.test import TestCase

from .models import *
from .platron_client import *
from .email_client import send_application
from django.test.utils import override_settings
from datetime import datetime

# Create your tests here.
class PlatronTestCase(TestCase):

    def setUp(self):
        data = UserData(session="123")
        streamer = Streamer.objects.create(name="Vasya")
        tt1 = TicketType.objects.create(price=42, days_qty=1)
        tt2 = TicketType.objects.create(price=43, days_qty=2)
        order = Order.objects.create(id="77777-01", amount=128, email="dzenmassta@gmail.com")
        OrderItem.objects.create(order=order, ticket_type=tt1, quantity=1, amount=42, streamer=streamer)
        OrderItem.objects.create(order=order, ticket_type=tt2, quantity=2, amount=86)
        order.set_paid(datetime.now())
        pass

    """
    def test_platron_init_and_cancel(self):
        txn = init_payment(Order.objects.first())
        print(txn.redirect_url)
        txn.save()
        pers = PlatronPayment.objects.first()
        self.assertEqual(txn, pers)
    """

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
        result = OrderItem.summary_by_uid(streamer.uniqUrl, end = datetime.now())
        print("Summary: {}".format(result))

    def test_stats(self):
        streamer = Streamer.objects.get(name="Vasya")
        result = OrderItem.items_by_uid(streamer.uniqUrl, end = datetime.now())
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
                "photo": streamer.photo.url
            },
            "summary": list(summary),
            "items": list(items)
        }
        print("Json: {}".format(json.dumps(stats, cls=DjangoJSONEncoder)))
