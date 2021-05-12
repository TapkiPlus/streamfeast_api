from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.conf import settings
from .models import Ticket, OrderItem
from django.db import transaction
from datetime import datetime

import logging

SOURCE_EMAIL = 'tickets@streamfest.ru'


def order_html(order, tickets):
    htmly = get_template('../template/apply.html')
    ctx = {
        'order': order,
        'tickets': tickets
    }
    return htmly.render(ctx)

def ticket_html(ticket): 
    tt = ticket.order_item.ticket_type
    html_template = '../template/1day.html' if tt.days_qty == 1 else '../template/2days.html'
    htmly = get_template(html_template)
    ctx = {
        'ticket': ticket,
        'site_url': settings.SITE_URL
    }
    return htmly.render(ctx)


def send_application(order):
    tickets = Ticket.objects.filter(order=order)
    order_header = 'Стримфест 2021 — подтверждение заказа №{}'.format(order.id)
    order_content = order_html(order, tickets)
    
    msg = EmailMessage(order_header, order_content, SOURCE_EMAIL, [order.email])
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
            ticket_header = 'Билет №{} на Стримфест 2021 — 17–18 июля'.format(ticket.ticket_id)
            ticket_content = ticket_html(ticket)
            msg = EmailMessage(ticket_header, ticket_content, SOURCE_EMAIL, [order.email])
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send() # potentially unsafe method
            ticket.when_sent = datetime.now()
        except Exception as err: 
            logging.exception("Failed to send ticket", exc_info = True)
            ticket.send_attempts +=1 
        ticket.save()



