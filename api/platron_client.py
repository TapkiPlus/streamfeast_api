from xml.dom import minidom

from dateutil import parser
from platron.callback import Callback
from platron.request.clients.post_client import PostClient
from platron.request.request_builders.init_payment_builder import InitPaymentBuilder

from .email_client import send_application
from .models import PlatronPayment, Order

MERCHANT_ID = "11251"
MERCHANT_KEY = "putyhipurynyrexe"

CHECK_PATH = "payment_check"
RESULT_PATH = "payment_result"

client = PostClient(MERCHANT_ID, MERCHANT_KEY)


def init_payment(order):
    request = InitPaymentBuilder(order.amount, 'Оплата билетов')
    request.add_order_id(str(order.id))
    ###################################
    # TODO: remove when in production #
    # request.add_testing_mode()      #
    ###################################
    raw = client.request(request)
    doc = parse_response(raw)
    tx = parse_create_tx(doc)
    return tx

def payment_check(params):
    callback = Callback(CHECK_PATH, MERCHANT_KEY)
    # check if order is still not paid
    # order_available = True
    if callback.validate_sig(params):
        return callback.response_ok(params)
    else:
        return callback.response_error(params, 'Неправильная подпись')


def get_decimal(text):
    try: return float(text)
    except: return None 


def get_int(text):
    try: return int(text)
    except: return None 


def payment_result(params):
    callback = Callback(RESULT_PATH, MERCHANT_KEY)
    if callback.validate_sig(params):
        try:
            order_id = params["pg_order_id"]
            order = Order.objects.get(id=order_id)
            order.payment_system = params["pg_payment_system"]
            order.card_pan = params.get("pg_card_pan", "")
            order.failure_code = get_int(params.get("pg_failure_code", "0"))
            order.failure_desc = params.get("pg_failure_description")
            date = parser.parse(params["pg_payment_date"])
            if params["pg_result"] == "1":
                order.set_paid(date)
                send_application(order)
            else:
                order.set_unpaid()
            return callback.response_ok(params)
        except:
            return callback.response_error(params, 'Не удалось обработать платеж')
    else:
        return callback.response_error(params, 'Неправильная подпись')


##########
# parser ######################################################################################################

def get_text(elem, key):
    nodelist = elem.getElementsByTagName(key)
    return get_text_0(nodelist)


def get_text_0(nodes):
    rc = []
    for node in nodes:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
        else:
            rc.append(get_text_0(node.childNodes))
    return ''.join(rc)


def parse_response(raw_xml):
    doc = minidom.parseString(raw_xml)
    return doc.getElementsByTagName("response")[0]


def parse_create_tx(elem):
    pg_status = get_text(elem, "pg_status") == "ok"
    pg_payment_id = get_text(elem, "pg_payment_id")
    pg_redirect_url = get_text(elem, "pg_redirect_url")
    return PlatronPayment(id=pg_payment_id, status=pg_status, redirect_url=pg_redirect_url)
