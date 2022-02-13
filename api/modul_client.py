from dataclasses import dataclass
from django.conf import settings

import dataclasses
import hashlib
import base64
import random, string
import json
import requests
from time import time
from dateutil import parser
from .email_client import send_application

from api.models import ModulTxnForm, Order, OrderItem

__testing_mode = 1
__api_url = "https://pay.modulbank.ru/pay"


__secret_key = settings.PAYMENT_KEY
__host = settings.SITE_URL


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

    def randomStr(size: int): 
        ''.join(random.choice(string.ascii_letters) for x in range(size))

    receipt_items = map(lambda oi: dataclasses.asdict(to_receipt_item(oi)), order_items)

    txn_params = {       
        "salt": randomStr(32),
        "merchant": settings.PAYMENT_MERCHANT_ID,
        "receipt_contact": 'tickets@streamfest.ru',
        "testing": 1 if __testing_mode else 0,
        "order_id": order.id,
        "receipt_items": json.dumps(list(receipt_items)),
        "amount": order.amount,
        "client_phone": order.phone,
        "client_email": order.email,
        "callback_url": "{}/api/payment_result".format(__host),
        "description": "Заказ №{}".format(order.id),
        "unix_timestamp": int(time()),
        "success_url": "{}/success-page?pg_order_id={}".format(__host, order.id)
    }

    # make signature afterwards
    signature = get_signature(txn_params)
    txn_params["signature"] = signature

    resp = requests.post(__api_url, data = txn_params, allow_redirects=False)
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




