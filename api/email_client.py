from django.core.mail import EmailMessage
from .models import Order, Ticket

SOURCE_EMAIL = 'from@streamfest.ru'

def send_tickets(order): 
    tickets = Ticket.objects.filter(order = order)
    email = EmailMessage( 'Your tickets', 'Are attached to this message.', SOURCE_EMAIL, [order.email])
    for ticket in tickets:
        filename = f'{t.ticket_id}.pdf'
        file = t.pdf(filename = filename)
        email.attach_file(filename)
    email.send()
