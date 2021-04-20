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
from django.template.loader import get_template
from pytils.translit import slugify


class PlatronPayment(models.Model):
    id = models.CharField("PaymentId", max_length=32, blank=False, primary_key=True, editable=False, null=False)
    status = models.BooleanField("Status")
    redirect_url = models.CharField("RedirectURL", max_length=255, blank=False, unique=True, editable=False, null=False)


class Faq(models.Model):
    order_number = models.IntegerField('№ П/П', default=100)
    question = models.CharField('Вопрос', max_length=255, blank=False, null=True)
    answer = RichTextUploadingField('Ответ', max_length=255, blank=False, null=True)

    def __str__(self):
        return f'{self.id} Вопрос : {self.question}'

    class Meta:
        ordering = ('order_number',)
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ"


class HowTo(models.Model):
    order_number = models.IntegerField('№ П/П', default=100)
    question = models.TextField('Вопрос', blank=False, null=True)
    answer = RichTextUploadingField('Ответ', blank=False, null=True)
    icon = models.ImageField('Иконка', upload_to='icons/', blank=False, null=True)
    is_open_by_default = models.BooleanField('Открыто по умолчанию', default=False)

    def __str__(self):
        return f'{self.id} Вопрос : {self.question}'

    class Meta:
        ordering = ('order_number',)
        verbose_name = "Как стать участником"
        verbose_name_plural = "Как стать участником"


class SocialIcon(models.Model):
    name = models.CharField('Название сети', max_length=255, blank=False, null=True)
    icon = models.ImageField('Обложка', upload_to='speaker_img/', blank=False, null=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = "Иконка соц. сети"
        verbose_name_plural = "Иконки соц. сетей"


class Streamer(models.Model):
    orderPP = models.IntegerField('Номер ПП', default=10)
    nickName = models.CharField('Ник', max_length=255, blank=False, null=True, db_index=True)
    name = models.CharField('Имя Фамилия', max_length=255, blank=False, null=True)
    photo = models.ImageField('Аватар', upload_to='speaker_img/', blank=False, null=True)
    pageHeader = models.ImageField('Обложка', upload_to='speaker_img/', blank=False, null=True)
    nickNameSlug = models.CharField(max_length=255, blank=True, null=True, unique=True, db_index=True)
    about = RichTextUploadingField('Описание', blank=True, null=True)
    streaming = RichTextUploadingField('Что стримит', blank=True, null=True)
    isAtHome = models.BooleanField('Отображать на главной?', default=False)
    sells = models.BooleanField('Отображать блок билетов и подпись?', default=True)
    isActive = models.BooleanField('Отображать?', default=False) 
    uniqUrl = models.CharField('Хеш для ссылки (/star/stats/)', max_length=100, blank=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        slug = slugify(self.nickName)
        if not self.nickNameSlug:
            testSlug = Streamer.objects.filter(nickNameSlug=slug)
            slugRandom = ''
            if testSlug:
                slugRandom = '-' + ''.join(choices(string.ascii_lowercase + string.digits, k=2))
            self.nickNameSlug = slug + slugRandom
        self.uniqUrl = self.nickNameSlug + '-' + ''.join(choices(string.ascii_lowercase + string.digits, k=10))
        super(Streamer, self).save(*args, **kwargs)

    def __str__(self):
        return f'Стример : {self.name}'

    class Meta:
        verbose_name = "Стример"
        verbose_name_plural = "Стримеры"


class SocialLink(models.Model):
    icon = models.ForeignKey(SocialIcon, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Иконка')
    user = models.ForeignKey(Streamer, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Стример',
                             related_name='links')
    link = models.CharField('Ссылка', max_length=255, blank=True, null=True)

    class Meta:
        ordering = ("id",)


class TicketType(models.Model):
    class Days(models.IntegerChoices):
        ONE = 1
        TWO = 2

    price = models.IntegerField('Цена', blank=False, null=True)
    days_qty = models.PositiveSmallIntegerField('На сколько дней?', choices=Days.choices, default=Days.ONE)

    def __str__(self):
        if self.days_qty == 1:
            return f'Билет на один день : {self.price}'
        else:
            return f'Билет на два дня : {self.price}'

    class Meta:
        ordering = ('price',)
        verbose_name = "Тип билета"
        verbose_name_plural = "Типы билетов"


class Cart(models.Model):
    session = models.CharField('Сессия', max_length=255, blank=True, null=True)
    total_price = models.IntegerField('Стоимось корзины', default=0)

    def __str__(self):
        return f'Стоимость корзины : {self.total_price}'

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"


class CartItem(models.Model):
    parent = models.ForeignKey(Cart, on_delete=models.CASCADE, null=False, blank=False, verbose_name='Корзина')
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Билет')
    streamer = models.ForeignKey(Streamer, on_delete=models.CASCADE, null=True, blank=True, verbose_name='От кого')
    quantity = models.IntegerField('Количество', default=0)

    def __str__(self):
        if self.streamer:
            if self.ticket_type.days_qty == 1:
                return f'Билет на один день от: {self.streamer.name}'
            if self.ticket_type.days_qty == 2:
                return f'Билет на два дня: {self.streamer.name}'
        else:
            if self.ticket_type.days_qty == 1:
                return f'Билет на один день'
            if self.ticket_type.days_qty == 2:
                return f'Билет на два дня'

    class Meta:
        verbose_name = "Билет в корзине"
        verbose_name_plural = "Билеты в корзинах"

 
class UserData(models.Model):
    session = models.CharField('Сессия', max_length=255, blank=False, unique=True)
    firstname = models.CharField('Имя', max_length=255, blank=True, null=True)
    lastname = models.CharField('Фамилия', max_length=255, blank=True, null=True)
    email = models.CharField('Email', max_length=255, blank=True, null=True)
    phone = models.CharField('Телефон', max_length=255, blank=True, null=True)
    wentToCheckout = models.IntegerField('Количество переходов к оформлению билета', default=0) #done
    returnedToShop = models.IntegerField('Количество переходов на покупку билета снова', default=0) #done
    clickedPay = models.IntegerField('Количество нажатий на оплатить', default=0) #done
    tryedToPayAgain = models.IntegerField('Количество нажатий попробовать еще раз', default=0) #done
    clickedTechAssistance = models.IntegerField('Количество кликов на техпомощь', default=0) #done

    def __str__(self):
        return f'{self.firstname}'

    class Meta:
        verbose_name = "Данные пользователя"
        verbose_name_plural = "Данные пользователей"


class Order(models.Model):
    id = models.TextField("ID", primary_key=True)
    firstname = models.CharField('Имя', max_length=255, blank=True, null=True)
    lastname = models.CharField('Фамилия', max_length=255, blank=True, null=True)
    email = models.CharField('Email', max_length=255, blank=False, null=False)
    phone = models.CharField('Телефон', max_length=255, blank=True, null=True)
    is_paid = models.BooleanField('Оплачен?', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField('Стоимось', default=0)

    @transaction.atomic
    def set_paid(self):
        if self.is_paid == False:
            self.is_paid = True
            items = OrderItem.objects.filter(order=self)
            index = 0
            for item in items:
                for i in range(item.quantity):
                    index += 1
                    id = '{}-{:02d}'.format(self.id, index)
                    Ticket.objects.create(ticket_id=id, order_item=item, order=self)
            self.save()

    def __str__(self):
        return f'Заказ от {self.created_at}'

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    ticket_type = models.ForeignKey(TicketType, on_delete=models.RESTRICT, null=True, blank=True, verbose_name='Билет')
    quantity = models.IntegerField('Количество', default=1)
    streamer = models.ForeignKey(Streamer, on_delete=models.CASCADE, null=True, blank=True, verbose_name='От кого')
    amount = models.IntegerField('Стоимось', default=0)

    def __str__(self):
        return f'Билет на {"1 день" if self.ticket.is_one_day else "2 дня"} - {self.streamer.name if self.streamer else ""}'


class Ticket(models.Model):
    ticket_id = models.TextField("ID", primary_key=True)
    ticket_uuid = models.UUIDField("QR-code", default=uuid.uuid4)
    order_item = models.ForeignKey(OrderItem, on_delete=models.RESTRICT, null=False, verbose_name='Позиция')
    order = models.ForeignKey(Order, on_delete=models.RESTRICT, null=False, verbose_name='Заказ')
    when_cleared = models.DateTimeField(null=True, verbose_name='Дата и время погашения')

    def __str__(self):
        tt = self.order_item.ticket_type
        item = self.order_item
        ord = self.order
        return f'Ticket {self.ticket_id} by {item.streamer} for {tt.days_qty} days'

    def pdf(self, filename=False):
        template = get_template('../templates/ticket.html')
        image = qr_code(str(self.ticket_uuid))
        encoded = str(base64.b64encode(image))[2:-1]
        html = template.render({'t': self, 'qr': encoded})
        options = {
            'page-size': 'Letter',
            'encoding': "UTF-8",
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
    image = models.ImageField("Картинка", blank=False, null=False, upload_to='activity_images/')
    icon = models.ImageField("Иконка", blank=False, null=False, upload_to='activity_icons/')
    place = models.ForeignKey(Place, on_delete=models.RESTRICT, null=False, verbose_name="Место")
    streamer = models.ForeignKey(Streamer, on_delete=models.RESTRICT, null=True, verbose_name="Участник")

    class Meta:
        verbose_name = "Активность"
        verbose_name_plural = "Активности"


