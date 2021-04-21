from django.test import TestCase

from .models import *
from .platron_client import *
from .email_client import send_application
from django.test.utils import override_settings

# Create your tests here.
class PlatronTestCase(TestCase):

    def setUp(self):
        data = UserData(session="123")
        tt1 = TicketType.objects.create(price=42, days_qty=1)
        tt2 = TicketType.objects.create(price=43, days_qty=2)
        order = Order.objects.create(id="77777-01", amount=128, email="dzenmassta@gmail.com")
        OrderItem.objects.create(order=order, ticket_type=tt1, quantity=1, amount=42)
        OrderItem.objects.create(order=order, ticket_type=tt2, quantity=2, amount=86)
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
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
    def test_order_paid(self):
        order = Order.objects.last()
        order.set_paid()
        send_application(order)
        # tickets = Ticket.objects.all()
        # for t in tickets:
        #     file = t.pdf(filename=f'{t.ticket_id}.pdf')
        #     print("FFF")
        #     print(file)
