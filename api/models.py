import base64
import io
import string
import uuid
from random import choices

import pdfkit
from .services import qr_code
from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.db import transaction
from django.db.models import Avg, Count, Min, Sum, F
from django.template.loader import get_template
from pytils.translit import slugify
from datetime import datetime, timedelta

ENTRY_ALLOWED = 0
ENTRY_FORBIDDEN_NO_SUCH_TICKET = 1
ENTRY_FORBIDDEN_ENTRY_ATTEMPTS_EXCEEDED = 2
ENTRY_FORBIDDEN_ALREADY_ENTRERED_TODAY = 3

class PlatronPayment(models.Model):
    id = models.CharField("PaymentId", max_length=32, blank=False, primary_key=True, editable=False, null=False)
    status = models.BooleanField("Status", editable=False)
    redirect_url = models.CharField("RedirectURL", max_length=255, blank=False, unique=True, editable=False, null=False)

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

class Faq(models.Model):
    order_number = models.IntegerField("№ П/П", default=100)
    question = models.CharField("Вопрос", max_length=255, blank=False, null=True)
    answer = RichTextUploadingField("Ответ", max_length=255, blank=False, null=True)

    def __str__(self):
        return f"{self.id} Вопрос : {self.question}"

    class Meta:
        ordering = ("order_number",)
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ"


class HowTo(models.Model):
    order_number = models.IntegerField("№ П/П", default=100)
    question = models.TextField("Вопрос", blank=False, null=True)
    answer = RichTextUploadingField("Ответ", blank=False, null=True)
    icon = models.ImageField("Иконка", upload_to="icons/", blank=False, null=True)
    is_open_by_default = models.BooleanField("Открыто по умолчанию", default=False)

    def __str__(self):
        return f"{self.id} Вопрос : {self.question}"

    class Meta:
        ordering = ("order_number",)
        verbose_name = "Как стать участником"
        verbose_name_plural = "Как стать участником"


class SocialIcon(models.Model):
    name = models.CharField("Название сети", max_length=255, blank=False, null=True)
    icon = models.ImageField("Обложка", upload_to="speaker_img/", blank=False, null=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Иконка соц. сети"
        verbose_name_plural = "Иконки соц. сетей"


class Streamer(models.Model):
    orderPP = models.IntegerField("Номер ПП", default=10)
    nickName = models.CharField("Ник", max_length=255, blank=False, null=True, db_index=True)
    name = models.CharField("Имя Фамилия", max_length=255, blank=False, null=True)
    email = models.CharField("Email", max_length=255, blank=True, null=True)
    photo = models.ImageField("Аватар", upload_to="speaker_img/", blank=False, null=True)
    pageHeader = models.ImageField("Обложка", upload_to="speaker_img/", blank=False, null=True)
    nickNameSlug = models.CharField(max_length=255, blank=True, null=True, unique=True, db_index=True)
    about = RichTextUploadingField("Описание", blank=True, null=True)
    streaming = RichTextUploadingField("Что стримит", blank=True, null=True)
    isAtHome = models.BooleanField("Отображать на главной?", default=False)
    sells = models.BooleanField("Отображать блок билетов и подпись?", default=True)
    isActive = models.BooleanField("Отображать?", default=False) 
    uniqUrl = models.TextField("Хеш для ссылки (/profile/)", default=uuid.uuid4, editable=False)

    def save(self, *args, **kwargs):
        if not self.nickNameSlug:
            self.nickNameSlug = slugify(self.nickName)
        super(Streamer, self).save(*args, **kwargs)

    def __str__(self):
        if self.nickName:
            return self.nickName
        elif self.name:
            return self.name
        else:
            return f"Стример: id = {self.id}"

    class Meta:
        verbose_name = "Стример"
        verbose_name_plural = "Стримеры"


class SocialLink(models.Model):
    icon = models.ForeignKey(SocialIcon, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Иконка")
    user = models.ForeignKey(Streamer, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Стример",
                             related_name="links")
    link = models.CharField("Ссылка", max_length=255, blank=True, null=True)

    class Meta:
        ordering = ("id",)


class TicketType(models.Model):
    class Days(models.IntegerChoices):
        ONE = 1
        TWO = 2

    price = models.IntegerField("Цена", blank=False, null=True)
    days_qty = models.PositiveSmallIntegerField("На сколько дней?", choices=Days.choices, default=Days.ONE)
 
    def __str__(self):
        if self.days_qty == 1:
            return f"Билет на один день : {self.price}"
        else:
            return f"Билет на два дня : {self.price}"

    class Meta:
        ordering = ("price",)
        verbose_name = "Тип билета"
        verbose_name_plural = "Типы билетов"


class Cart(models.Model):
    session = models.CharField("Сессия", max_length=255, blank=False, null=False, unique=True)
    total_price = models.IntegerField("Стоимось корзины", default=0)

    @transaction.atomic
    def calculate_cart_price(self):
        items = CartItem.objects.filter(parent=self)
        price = 0
        for i in items:
            price += i.quantity * i.ticket_type.price
        self.total_price = price
        self.save()

    @staticmethod
    @transaction.atomic
    def clear_cart(session_id):
        CartItem.objects.filter(parent__session=session_id).delete()
        Cart.objects.filter(session=session_id).delete()

    def __str__(self):
        return f"Стоимость корзины : {self.total_price}"

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"


class CartItem(models.Model):
    parent = models.ForeignKey(Cart, on_delete=models.CASCADE, null=False, blank=False, verbose_name="Корзина")
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Билет")
    streamer = models.ForeignKey(Streamer, on_delete=models.CASCADE, null=True, blank=True, verbose_name="От кого")
    quantity = models.IntegerField("Количество", default=0)

    def __str__(self):
        if self.streamer:
            if self.ticket_type.days_qty == 1:
                return f"Билет на один день от: {self.streamer.nickName}"
            if self.ticket_type.days_qty == 2:
                return f"Билет на два дня: {self.streamer.nickName}"
        else:
            if self.ticket_type.days_qty == 1:
                return f"Билет на один день"
            if self.ticket_type.days_qty == 2:
                return f"Билет на два дня"

    class Meta:
        ordering = ["id"]
        verbose_name = "Позиция корзины"
        verbose_name_plural = "Позиции в корзинах"

 
class UserData(models.Model):
    session = models.CharField("Сессия", max_length=255, blank=False, unique=True)
    firstname = models.CharField("Имя", max_length=255, blank=True, null=True)
    lastname = models.CharField("Фамилия", max_length=255, blank=True, null=True)
    email = models.CharField("Email", max_length=255, blank=True, null=True)
    phone = models.CharField("Телефон", max_length=255, blank=True, null=True)
    wentToCheckout = models.IntegerField("Количество переходов к оформлению билета", default=0) #done
    returnedToShop = models.IntegerField("Количество переходов на покупку билета снова", default=0) #done
    clickedPay = models.IntegerField("Количество нажатий на оплатить", default=0) #done
    tryedToPayAgain = models.IntegerField("Количество нажатий попробовать еще раз", default=0) #done
    clickedTechAssistance = models.IntegerField("Количество кликов на техпомощь", default=0) #done
    successfulPayments = models.IntegerField("Количество успешных платежей", default=0) #done
    failedPayments = models.IntegerField("Количество безуспешных платежей", default=0) #done

    def __str__(self):
        return f"{self.firstname}"

    @staticmethod
    def checkout(session_id):
        UserData.objects.filter(session=session_id).update(wentToCheckout=F("wentToCheckout") + 1)

    @staticmethod
    def payment_success(session_id):
        UserData.objects.filter(session=session_id).update(successfulPayments=F("successfulPayments") + 1)

    @staticmethod
    def payment_failed(session_id):
        UserData.objects.filter(session=session_id).update(failedPayments=F("failedPayments") + 1)
        


    class Meta:
        verbose_name = "Данные пользователя"
        verbose_name_plural = "Данные пользователей"


class Order(models.Model):
    id = models.TextField("ID", primary_key=True)
    session = models.CharField("Сессия", max_length=255, blank=False)
    firstname = models.CharField("Имя", max_length=255, blank=True, null=True)
    lastname = models.CharField("Фамилия", max_length=255, blank=True, null=True)
    email = models.CharField("Email", max_length=255, blank=False, null=False)
    phone = models.CharField("Телефон", max_length=255, blank=True, null=True)
    when_paid = models.DateTimeField("Дата и время оплаты", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField("Стоимось", default=0)
    payment_system = models.TextField("Платежная система", null=True)
    card_pan = models.TextField("Номер карты", null=True)
    failure_code = models.IntegerField("Код ошибки", null=True)
    failure_desc = models.TextField("Описание ошибки", null=True)

    def get_recently_paid(order_id): 
        since = datetime.now() - timedelta(minutes=1)
        return Order.objects.get(id=order_id, when_paid__gt=since)


    @staticmethod
    @transaction.atomic
    def create(session_id, data): 
        cart = Cart.objects.get(session=session_id)
        user_data = UserData.objects.get(session=session_id)
        order_id = "{:05d}-{:02d}".format(user_data.id, user_data.wentToCheckout)
        print("Creating order id {}".format(order_id))
        new_order = Order.objects.create(
            id=order_id,
            session=session_id,
            firstname=data.get('firstname'),
            lastname=data.get('lastname'),
            email=data.get('email'),
            phone=data.get('phone'),
            amount=cart.total_price
        )
        cart_items = CartItem.objects.filter(parent=cart)
        index = 0
        for i in cart_items:
            index += 1
            OrderItem.objects.create(
                order=new_order,
                ticket_type=i.ticket_type,
                quantity=i.quantity,
                streamer=i.streamer,
                amount=i.quantity * i.ticket_type.price
            )
        return new_order

    @transaction.atomic
    def set_paid(self, date):
        if self.when_paid is None:
            Cart.clear_cart(self.session)
            UserData.payment_success(self.session)
            self.when_paid = date
            items = OrderItem.objects.filter(order=self)
            index = 0
            for item in items:
                for i in range(item.quantity):
                    index += 1
                    id = "{}-{:02d}".format(self.id, index)
                    Ticket.objects.create(ticket_id=id, order_item=item, order=self)
            self.save()

    def set_unpaid(self):
        if self.when_paid is None: 
            UserData.payment_failed(self.session)


    def __str__(self):
        return f"Заказ {self.id} от {self.firstname} оплачен: {self.when_paid}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    ticket_type = models.ForeignKey(TicketType, on_delete=models.RESTRICT, null=True, blank=True, verbose_name="Билет")
    quantity = models.IntegerField("Количество", default=1)
    streamer = models.ForeignKey(Streamer, on_delete=models.CASCADE, null=True, blank=True, verbose_name="От кого")
    amount = models.IntegerField("Стоимось", default=0)

    class Meta:
        ordering = ["id"]
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказов"

    @staticmethod
    def items_by_uid(uid, start = None, end = None):
        raw = OrderItem.objects
        if start: 
            raw = raw.filter(order__when_paid__gt=start)
        if end:
            raw = raw.filter(order__when_paid__lt=end)
        qs = raw.filter( \
            order__when_paid__isnull=False, \
            streamer__uniqUrl=uid \
        ) \
         .annotate(order_pk = F("order__id"), when_paid = F("order__when_paid"), qty = F("quantity"), name = F("order__firstname"), email = F("order__email")) \
         .values("order_pk", "when_paid", "qty", "name", "email") \
         .order_by("-when_paid")
         
        return qs

    @staticmethod
    def summary_by_uid(uid, start = None, end = None):
        raw = OrderItem.objects
        if start:
            raw = raw.filter(order__when_paid__gt=start)
        if end:
            raw = raw.filter(order__when_paid__lt=end)
        qs = raw.filter( \
            order__when_paid__isnull=False, \
            streamer__uniqUrl=uid \
        ) \
         .values("ticket_type__days_qty") \
         .annotate(type = F("ticket_type__days_qty"), qty = Sum("quantity"), amt = Sum("amount")) \
         .values("type", "qty", "amt") \
         .order_by("type")

        return qs

    def __str__(self):
        start = "1 день" if self.ticket_type.days_qty == 1 else "2 дня"
        end = f" от {self.streamer}" if self.streamer else ""
        return f'Билет на {start}{end}'


class Ticket(models.Model):
    ticket_id = models.TextField("ID", primary_key=True)
    ticket_uuid = models.UUIDField("QR-code", default=uuid.uuid4)
    order_item = models.ForeignKey(OrderItem, on_delete=models.RESTRICT, null=False, verbose_name="Позиция")
    order = models.ForeignKey(Order, on_delete=models.RESTRICT, null=False, verbose_name="Заказ")
    when_cleared = models.DateTimeField("Дата и время погашения", null=True)
    when_sent = models.DateTimeField("Дата и время отправки", null=True)
    send_attempts = models.SmallIntegerField("Количество попыток отправки", null=False, default=0)
    checkin_count = models.SmallIntegerField("Успешных попыток прохода", null=False, default=0)
    checkin_last = models.DateTimeField("Дата и время последнего входа", null=True)

    def __str__(self):
        tt = self.order_item.ticket_type
        item = self.order_item
        return f"Ticket {self.ticket_id} by {item.streamer} for {tt.days_qty} days"

    def checkin_allowed(self): 
        ttype = self.order_item.ticket_type
        today = datetime.now().day
        if self.checkin_count >= ttype.days_qty: 
            return ENTRY_FORBIDDEN_ENTRY_ATTEMPTS_EXCEEDED
        elif self.checkin_last is not None and self.checkin_last.day() == today:
            return ENTRY_FORBIDDEN_ALREADY_ENTRERED_TODAY
        else:
            return ENTRY_ALLOWED


    def checkin(self): 
        result = self.checkin_allowed()
        if result == ENTRY_ALLOWED:
            Ticket.objects \
                .filter(ticket_id=self.ticket_id) \
                .update(checkin_count=F("checkin_count") + 1, checkin_last=datetime.now())
        return result
        

    def pdf(self, filename=False):
        template = get_template("../templates/ticket.html")
        image = qr_code(str(self.ticket_uuid))
        encoded = str(base64.b64encode(image))[2:-1]
        html = template.render({"t": self, "qr": encoded})
        options = {
            "page-size": "Letter",
            "encoding": "UTF-8",
        }
        return pdfkit.from_string(html, filename, options)

    class Meta:
        verbose_name = "Билет"
        verbose_name_plural = "Билеты"


class Subscribe(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"


class Place(models.Model): 
    id = models.AutoField("ID", primary_key=True)
    name = models.TextField("Место")
    level = models.TextField("Уровень")

    class Meta:
        verbose_name = "Место"
        verbose_name_plural = "Места"


class Activity(models.Model): 
    day = models.IntegerField("День")
    start = models.TextField("Начало")
    end = models.TextField("Окончание")
    title = models.TextField("Название")
    description = models.TextField("Описание")
    image = models.ImageField("Картинка", blank=False, null=False, upload_to="activity_images/")
    icon = models.ImageField("Иконка", blank=False, null=False, upload_to="activity_icons/")
    place = models.ForeignKey(Place, on_delete=models.RESTRICT, null=False, verbose_name="Место")
    streamer = models.ForeignKey(Streamer, on_delete=models.RESTRICT, null=True, verbose_name="Участник")

    class Meta:
        verbose_name = "Активность"
        verbose_name_plural = "Активности"


