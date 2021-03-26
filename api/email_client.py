from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

from .models import Ticket, OrderItem

SOURCE_EMAIL = 'tickets@streamfest.ru'

def send_tickets(order):
    tickets = Ticket.objects.filter(order=order)
    items = OrderItem.objects.filter(order=order)

    ctx = {
        'order': order,
        'items': items
    }

    plaintext = get_template('../templates/email_tickets.txt')
    text_content = plaintext.render(ctx)

    htmly = get_template('../templates/email_tickets.html')
    html_content = htmly.render(ctx)

    msg = EmailMultiAlternatives('Билеты на стримфест', text_content, SOURCE_EMAIL, [order.email])
    msg.attach_alternative(html_content, 'text/html')

    for t in tickets:
        filename = f'{t.ticket_id}.pdf'
        file = t.pdf(filename=filename)
        msg.attach_file(filename)

    msg.send()
