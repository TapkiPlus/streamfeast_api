from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.db.models.signals import post_save
from pytils.translit import slugify
import pyqrcode
from random import choices
import string
from streamfeast_api.settings import BASE_DIR, BASE_URL
import uuid


class Faq(models.Model):
    order_number = models.IntegerField('№ П/П',
                                       default=100)
    question = models.CharField('Вопрос',
                                max_length=255,
                                blank=False,
                                null=True)
    answer = RichTextUploadingField('Ответ',
                                    max_length=255,
                                    blank=False,
                                    null=True)

    def __str__(self):
        return f'{self.id} Вопрос : {self.question}'

    class Meta:
        ordering = ('order_number',)
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ"


class HowTo(models.Model):
    order_number = models.IntegerField('№ П/П',
                                       default=100)
    question = models.TextField('Вопрос',
                                blank=False,
                                null=True)
    answer = RichTextUploadingField('Ответ',
                                    blank=False,
                                    null=True)
    icon = models.ImageField('Иконка',
                             upload_to='icons/',
                             blank=False,
                             null=True)
    is_open_by_default = models.BooleanField('ЭТА ШТУКА ОТКРЫТА ПО УМОЛЧАНИЮ?;))',
                                             default=False)

    def __str__(self):
        return f'{self.id} Вопрос : {self.question}'

    class Meta:
        ordering = ('order_number',)
        verbose_name = "Как стать участником"
        verbose_name_plural = "Как стать участником"


class SocialIcon(models.Model):
    name = models.CharField('Название сети',
                            max_length=255,
                            blank=False,
                            null=True)
    icon = models.ImageField('Обложка',
                             upload_to='speaker_img/',
                             blank=False,
                             null=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = "Иконка соц. сети"
        verbose_name_plural = "Иконки соц. сетей"


class Streamer(models.Model):
    orderPP = models.IntegerField('Номер ПП', default=10)
    nickName = models.CharField('Ник',
                                max_length=255,
                                blank=False,
                                null=True,
                                db_index=True)
    name = models.CharField('Имя Фамилия',
                            max_length=255,
                            blank=False,
                            null=True)
    photo = models.ImageField('Аватар',
                              upload_to='speaker_img/',
                              blank=False,
                              null=True)
    pageHeader = models.ImageField('Обложка',
                                   upload_to='speaker_img/',
                                   blank=False,
                                   null=True)
    nickNameSlug = models.CharField(max_length=255,
                                    blank=True,
                                    null=True,
                                    unique=True,
                                    db_index=True,
                                    editable=False)

    about = RichTextUploadingField('Описание',
                                   blank=True,
                                   null=True)
    streaming = RichTextUploadingField('Что стримит',
                                       blank=True,
                                       null=True)
    isAtHome = models.BooleanField('Отображать на главной?',
                                   default=False)
    isActive = models.BooleanField('Отображать?',
                                   default=False)
    uniqUrl = models.CharField('Хеш для ссылки (/star/stats/)',
                               max_length=100,
                               blank=True,
                               null=True,
                               editable=False)

    def save(self, *args, **kwargs):
        slug = slugify(self.nickName)
        if not self.nickNameSlug:
            testSlug = Streamer.objects.filter(nickNameSlug=slug)
            slugRandom = ''
            if testSlug:
                slugRandom = '-' + ''.join(choices(string.ascii_lowercase + string.digits, k=2))
            self.nickNameSlug = slug + slugRandom
        if not self.uniqUrl:
            self.uniqUrl = self.nickNameSlug + '-' + ''.join(choices(string.ascii_lowercase + string.digits, k=10))
        super(Streamer, self).save(*args, **kwargs)

    def __str__(self):
        return f'Стример : {self.name}'

    class Meta:
        verbose_name = "Стример"
        verbose_name_plural = "Стримеры"


class SocialLink(models.Model):
    icon = models.ForeignKey(SocialIcon,
                             on_delete=models.CASCADE,
                             null=True,
                             blank=True,
                             verbose_name='Иконка')
    user = models.ForeignKey(Streamer,
                             on_delete=models.CASCADE,
                             null=True,
                             blank=True,
                             verbose_name='Стример',
                             related_name='links')
    link = models.CharField('Ссылка', max_length=255, blank=True, null=True)


class Ticket(models.Model):
    price = models.IntegerField('Цена',
                                blank=False,
                                null=True)
    is_one_day = models.BooleanField('На один день?',
                                     default=False)
    is_two_day = models.BooleanField('На два дня?',
                                     default=False)

    def __str__(self):
        if self.is_one_day:
            return f'Билет на один день : {self.price}'
        if self.is_two_day:
            return f'Билет на два дня : {self.price}'

    class Meta:
        ordering = ('price',)
        verbose_name = "Билет"
        verbose_name_plural = "Билеты"


class CartItem(models.Model):
    t_id = models.CharField(max_length=255,
                            blank=True,
                            null=True)
    ticket = models.ForeignKey(Ticket,
                               on_delete=models.CASCADE,
                               null=True,
                               blank=True,
                               verbose_name='Билет')
    streamer = models.ForeignKey(Streamer,
                                 on_delete=models.CASCADE,
                                 null=True,
                                 blank=True,
                                 verbose_name='От кого')
    quantity = models.IntegerField('Количество',
                                   default=1)

    def __str__(self):
        if self.streamer:
            if self.ticket.is_one_day:
                return f'Билет на один день от : {self.streamer.name}'
            if self.ticket.is_two_day:
                return f'Билет на два дня : {self.streamer.name}'
        else:
            if self.ticket.is_one_day:
                return f'Билет на один день '
            if self.ticket.is_two_day:
                return f'Билет на два дня '

    class Meta:
        verbose_name = "Билет в корзине"
        verbose_name_plural = "Билеты в корзинах"


class Cart(models.Model):
    session = models.CharField('Сессия',
                               max_length=255,
                               blank=True,
                               null=True)
    tickets = models.ManyToManyField(CartItem,
                                     blank=True,
                                     verbose_name='Билеты')
    total_price = models.IntegerField('Стоимось корзины',
                                      default=0)

    def __str__(self):
        return f'Стоимость корзины : {self.total_price}'
    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"


class OrderItem(models.Model):
    u_id = models.UUIDField(null=True,
                            blank=True)
    o_id = models.UUIDField(null=True,
                            blank=True)
    ticket = models.ForeignKey(Ticket,
                               on_delete=models.CASCADE,
                               null=True,
                               blank=True,
                               verbose_name='Билет')
    streamer = models.ForeignKey(Streamer,
                                 on_delete=models.CASCADE,
                                 null=True,
                                 blank=True,
                                 verbose_name='От кого')
    quantity = models.IntegerField('Количество',
                                   default=1)
    qr = models.ImageField('QR',
                           blank=True,
                           null=True,
                           upload_to='ticket_qr/')


class Order(models.Model):
    u_id = models.UUIDField(default=uuid.uuid4)
    name = models.CharField('Имя',
                            max_length=255,
                            blank=True,
                            null=True)
    family = models.CharField('Фамилия',
                              max_length=255,
                              blank=True,
                              null=True)
    email = models.CharField('Email',
                             max_length=255,
                             blank=True,
                             null=True)
    phone = models.CharField('Телефон',
                             max_length=255,
                             blank=True,
                             null=True)
    tickets = models.ManyToManyField(OrderItem,
                                     blank=True,
                                     verbose_name='Билеты')
    is_payed = models.BooleanField('Оплачен?',
                                   default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Заказ от {self.created_at}'

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

def createOrderItem(sender, instance, created, **kwargs):
    if created:
        print('Create QR')
        codeQR = str(uuid.uuid4())
        instance.u_id = codeQR
        url = pyqrcode.create(f'{BASE_URL}/ticket/{codeQR}')
        url.png(f'{BASE_DIR}/media/ticket_qr/{codeQR}.png', scale=10)
        instance.qr = f'/ticket_qr/{codeQR}.png'
        instance.save()


post_save.connect(createOrderItem, sender=OrderItem)


class Subscribe(models.Model):
    email = models.EmailField(unique=True)
    def __str__(self):
        return self.email
    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
