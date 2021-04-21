from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.conf import settings
from .models import Ticket, OrderItem

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

    order_header = 'Стримфест: ваш заказ {} выполнен'.format(order.id)
    order_content = order_html(order, tickets)
    
    msg = EmailMessage(order_header, order_content, SOURCE_EMAIL, [order.email])
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send()

    for ticket in tickets:
        ticket_header = 'Билет №{} на стримфест'.format(ticket.ticket_id)
        ticket_content = ticket_html(ticket)

        msg = EmailMessage(ticket_header, ticket_content, SOURCE_EMAIL, [order.email])
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()

