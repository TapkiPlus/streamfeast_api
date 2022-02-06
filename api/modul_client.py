from dataclasses import dataclass
import dataclasses
import hashlib
import base64
from http.client import responses
import json
import requests
from time import time
from dateutil import parser
from .email_client import send_application

from api.models import ModulTxn, ModulTxnForm, Order, OrderItem

__api_url = "https://pay.modulbank.ru/pay"
__secret_key = "2618109CC214F9AFE0F855AE582A9BC4"
__testing_mode = 1
__host = "http://sf.tagobar.ru"

_items = {       
    "salt": 'dPUTLtbMfcTGzkaBnGtseKlcQymCLrYI',
    "merchant": 'c2659e97-cf26-421e-8a2e-91973e9bb5c2',
    "receipt_contact": 'test@mail.com',
}


def payment_result(params): 
    signature = get_signature(params)
    test_mode = bool(params["testing"])
    existing_signature = params["signature"]
    if test_mode or existing_signature == signature:
        try:
            # save txn
            form = ModulTxnForm(params)
            form.save()

            # set order paid
            order_id = params["order_id"]
            order = Order.objects.get(id=order_id)
            order.payment_system = params["payment_method"]
            order.card_pan = params.get("pan_mask", "")
            date = parser.parse(params["created_datetime"])
            if params["state"] == "COMPLETE":
                order.set_paid(date)
                send_application(order)
            else:
                order.set_unpaid()
            return 200
        except:
            print("Internal error")
            return 500
    else:
        print("Incorrect signature!")
        return 401


def make_purchase(order_id: str):

    order, order_items = Order.get_with_items(order_id)

    @dataclass(init=True)
    class ModulReceiptItem: 
        name: str
        quantity: int
        price: int
        sno: str = "usn_income"
        payment_object: str = "service"
        payment_method: str = "advance"
        vat: str = "none"    

    def to_receipt_item(oi: OrderItem):
        return ModulReceiptItem(str(oi), oi.quantity, oi.price)
    receipt_items = map(lambda oi: dataclasses.asdict(to_receipt_item(oi)), order_items)

    params_copy = _items.copy()
    params_copy["testing"] = 1 if __testing_mode else 0
    params_copy["order_id"] = order.id
    params_copy["receipt_items"] = json.dumps(list(receipt_items))
    params_copy["amount"] = order.amount
    params_copy["client_phone"] = order.phone
    params_copy["client_email"] = order.email
    params_copy["callback_url"] = "{}/api/payment_result".format(__host)
    params_copy["description"] = "Заказ №{}".format(order.id)
    params_copy["unix_timestamp"] = int(time())
    params_copy["success_url"] = "{}/success-page?pg_order_id={}".format(__host, order.id)

    for key, value in params_copy.items():
        print(key, ' : ', value)

    # make signature afterwards
    signature = get_signature(params_copy)
    params_copy["signature"] = signature

    resp = requests.post(__api_url, data = params_copy)
    print("Result: {}".format(resp.text))
    return resp


def get_signature(params: dict) -> str:

    def get_raw_signature(params):
        chunks = []

        for key in sorted(params.keys()):
            if key == 'signature':
                continue

            value = params[key]

            if not value:
                continue

            if isinstance(value, str):
                value = value.encode('utf8')
            else:
                value = str(value).encode('utf-8')

            value_encoded = base64.b64encode(value)
            chunks.append('%s=%s' % (key, value_encoded.decode()))

        raw_signature = '&'.join(chunks)
        return raw_signature

    '''Двойное шифрование sha1 на основе секретного ключа'''
    def double_sha1(data):
        sha1_hex = lambda s: hashlib.sha1(s.encode('utf-8')).hexdigest()
        digest = sha1_hex(__secret_key + sha1_hex(__secret_key + data))
        return digest


    return double_sha1(get_raw_signature(params))




