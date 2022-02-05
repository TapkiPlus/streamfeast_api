import hashlib
import base64
import json
import requests
from time import time

from api.models import Order, OrderItem

class ModulReceiptItem: 
    name: str
    quantity: int
    price: int
    sno: str = "usn_income"
    payment_object: str = "service"
    payment_method: str = "full_payment"
    vat: str = "none"

    def __init__(self, name: str, qty: int, price: int) -> None:
        self.name = name
        self.quantity = qty
        self.price = price

class ModulbankClient:

    _api_url = "https://pay.modulbank.ru/pay"

    _items = {       
        "salt": 'dPUTLtbMfcTGzkaBnGtseKlcQymCLrYI',
        # "amount": '973',
        "merchant": 'c2659e97-cf26-421e-8a2e-91973e9bb5c2',
        "receipt_contact": 'test@mail.com',
        # "receipt_items": '[{"discount_sum": 40, "name": "Товар 1", "payment_method": "full_prepayment", "payment_object": "commodity", "price": 48, "quantity": 10, "sno": "osn", "vat": "vat10"}, {"name": "Товар 2", "payment_method": "full_prepayment", "payment_object": "commodity", "price": 533, "quantity": 1, "sno": "osn", "vat": "vat10"}]',
    }

    __secret_key = "2618109CC214F9AFE0F855AE582A9BC4"

    def __init__(self, host: str, testing_mode: bool = True):
        self.__host = host
        # self.__secret_key = secret_key
        self.__testing_mode = testing_mode


    def make_purchase(self, order_id: str):
        order, order_items = Order.get_with_items(order_id)
        receipt_items = map(lambda oi: self.__to_receipt_item(oi), order_items)

        params_copy = self._items.copy()
        params_copy["testing"] = 1 if self.__testing_mode else 0
        params_copy["order_id"] = order.id
        params_copy["receipt_items"] = json.dumps(receipt_items)
        params_copy["amount"] = order.amount
        params_copy["client_phone"] = order.phone
        params_copy["client_email"] = order.email
        params_copy["callback_url"] = "{}/paid".format(self.__host)
        params_copy["description"] = "Заказ №{}".format(order.id)
        params_copy["unix_timestamp"] = int(time())
        params_copy["success_url"] = "{}/success-page?pg_order_id={}".format(self.__host, order.id)

        # for key, value in params_copy.items():
            # print(key, ' : ', value)

        # make signature afterwards
        signature = self.__get_signature(params_copy)
        params_copy["signature"] = signature

        r = requests.post(self._api_url, data = params_copy)
        print("Result: {}".format(r.text))


    def __str__(self):
        return "<ModulbankClient secret_key='…' host='{}' testing_mode='{}'>".format(self.__host, self.__testing_mode)

    def __to_receipt_item(oi: OrderItem):
        return ModulReceiptItem(str(oi), oi.quantity, oi.price)

    '''Вычисляем подпись (signature). Подпись считается на основе склеенной строки из отсортированного массива параметров, исключая из расчета пустые поля и элемент "signature" '''
    def __get_signature(self, params: dict) -> str:
        return self.__double_sha1(self.__get_raw_signature(params))

    def __get_raw_signature(self, params):
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
    def __double_sha1(self, data):
        sha1_hex = lambda s: hashlib.sha1(s.encode('utf-8')).hexdigest()
        digest = sha1_hex(self.__secret_key + sha1_hex(self.__secret_key + data))
        return digest
    
