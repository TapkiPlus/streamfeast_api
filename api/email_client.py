from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.conf import settings
from .models import Ticket, OrderItem, TicketType
from django.db import transaction
from django.utils import timezone

import logging

SOURCE_EMAIL = 'tickets@streamfest.ru'


def order_html(order, tickets):
    htmly = get_template('../template/apply.html')
    ctx = {
        'order': order,
        'tickets': tickets,
        'site_url': settings.SITE_URL
    }
    return htmly.render(ctx)

def ticket_html(ticket): 
    tt = ticket.ticket_type
    html_template = '../template/1day.html' if tt == TicketType.Types.REGULAR_ONE \
        else '../template/2days.html' if tt == TicketType.Types.REGULAR_TWO \
        else '../template/index.html' if tt == TicketType.Types.BLOGER \
        else '../template/invite.html' if tt == TicketType.Types.INVITE \
        else '../template/press.html' # assume this is press!
    htmly = get_template(html_template)
    ctx = {
        'ticket': ticket,
        'site_url': settings.SITE_URL
    }
    return htmly.render(ctx)


def send_application(order):
    tickets = Ticket.objects.filter(order=order)
    order_header = 'Стримфест 2022 — подтверждение заказа №{}'.format(order.id)
    order_content = order_html(order, tickets)

    bccs = ["info@streamfest.ru", "alyona@lisetskiy.com"]
    for t in tickets:
        streamer = t.streamer
        if streamer is not None:
            email = streamer.email
            if email is not None and email not in bccs:
                bccs.append(email)
    
    tos = [order.email]
    
    msg = EmailMessage(subject=order_header, body=order_content, from_email=SOURCE_EMAIL, to=tos, bcc=bccs)
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send()


def send_oldest(): 
    send_oldest_ticket()


@transaction.atomic
def send_oldest_ticket():
    qry = Ticket.objects.filter(when_sent__isnull=True, send_attempts__lt = 3)
    ticket = qry.order_by("order__when_paid", "ticket_id").first()

    if ticket is not None: 
        order = ticket.order
        try:
            ticket_header = 'Билет №{} на Стримфест 2022 — 25–26 июня'.format(ticket.ticket_id)
            ticket_content = ticket_html(ticket)
            msg = EmailMessage(ticket_header, ticket_content, SOURCE_EMAIL, [order.email])
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send() # potentially unsafe method
            ticket.when_sent = timezone.now()
        except Exception as err: 
            logging.exception("Failed to send ticket", exc_info = True)
            ticket.send_attempts +=1 
        ticket.save()



