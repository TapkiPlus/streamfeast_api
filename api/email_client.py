from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

from .models import Ticket

SOURCE_EMAIL = 'from@streamfest.ru'


def send_tickets(order):
    tickets = Ticket.objects.filter(order=order)

    ctx = Context({'order': order})

    plaintext = get_template('../templates/email_tickets.txt')
    text_content = plaintext.render(ctx)

    htmly = get_template('../templates/email_tickets.html')
    html_content = htmly.render(ctx)

    msg = EmailMessage('Билеты на стримфест', text_content, SOURCE_EMAIL, [order.email])
    msg.attach_alternative(html_content, 'text/html')

    for t in tickets:
        filename = f'{t.ticket_id}.pdf'
        file = t.pdf(filename=filename)
        msg.attach_file(filename)

    msg.send()
