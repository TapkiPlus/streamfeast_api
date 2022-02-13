from dataclasses import dataclass
from django.conf import settings

import logging
import dataclasses
import hashlib
import base64
import random
import string
import json
import requests
from time import time
from dateutil import parser
from .email_client import send_application

from api.models import ModulTxnForm, Order, OrderItem, UserData

__api_url = "https://pay.modulbank.ru/pay"


__testing_mode = settings.PAYMENT_TEST_MODE
__secret_key = settings.PAYMENT_KEY
__host = settings.SITE_URL


def payment_result(params):
    calculated_signature = get_signature(params)
    existing_signature = params["signature"]
    # allow testing only if enabled globally
    testing = params["testing"] == "1" and __testing_mode
    if testing or existing_signature == calculated_signature:
        try:
            # save txn (should it be one txn with set_paid?)
            txn: ModulTxn = ModulTxnForm(params).save()

            # then pay an order
            order = Order.set_paid_by(txn)

            # if everything was fine - send application
            send_application(order)
            return 200
        except Exception as e:
            logging.error(e, exc_info=True)
            return 500
    else:
        logging.warning(f"Incorrect signature value: Expected {calculated_signature} but got {existing_signature}")
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

    resp = requests.post(__api_url, data=txn_params, allow_redirects=False)
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
        def sha1_hex(s): return hashlib.sha1(s.encode('utf-8')).hexdigest()
        digest = sha1_hex(__secret_key + sha1_hex(__secret_key + data))
        return digest

    return double_sha1(get_raw_signature(params))
