from platron.request.request_builders.init_payment_builder import InitPaymentBuilder 
from platron.request.request_builders.get_registry_builder import GetRegistryBuilder 
from platron.request.request_builders.get_status_builder import GetStatusBuilder 
from platron.request.request_builders.do_capture_builder import DoCaptureBuilder 
from platron.request.request_builders.cancel_builder import CancelBuilder
from platron.request.clients.post_client import PostClient
from platron.sdk_exception import SdkException
from platron.callback import Callback
from .models import PlatronPayment, Order

from xml.dom import minidom

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
    request.add_testing_mode()        #
    ###################################
    raw = client.request(request)
    doc = parse_response(raw)
    tx = parse_create_tx(doc)
    return tx

"""
###################################
# Those methods aren't used yet.
#
def cancel_payment(payment_id):
    request = CancelBuilder(payment_id)
    raw = client.request(request)
    doc = parse_response(raw)
    print(raw) 

def get_payment_status(payment_id): 
    request = GetStatusBuilder(payment_id)
    try:
        response = client.request(request)
        print(response)
    except SdkException as msg:
        print(msg)

def do_capture(payment_id):
    request = DoCaptureBuilder('3334455')
    try:
        response = client.request(request)
        print(response)
    except SdkException as msg:
        print(msg)
###################################
"""

def payment_check(params): 
    callback = Callback(CHECK_PATH, MERCHANT_KEY)
    # check if order is still not paid
    # order_available = True
    if callback.validate_sig(params):
        return callback.response_ok(params)
    else:
        return callback.response_error(params, 'Неправильная подпись')

def payment_result(params): 
    callback = Callback(RESULT_PATH, MERCHANT_KEY)
    if callback.validate_sig(params):
        try: 
            order_id = params["pg_order_id"]
            print(order_id)
            order = Order.objects.get(id = order_id)
            print(order)
            order.set_paid()
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
    return PlatronPayment(id = pg_payment_id, status = pg_status, redirect_url = pg_redirect_url) 
