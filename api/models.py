from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from pytils.translit import slugify
from random import choices
import string


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
    question = models.CharField('Вопрос', max_length=255, blank=False, null=True)
    answer = RichTextUploadingField('Ответ', max_length=255, blank=False, null=True)
    icon = models.ImageField('Иконка)', upload_to='icons/', blank=False, null=True)

    def __str__(self):
        return f'{self.id} Вопрос : {self.question}'

    class Meta:
        ordering = ('order_number',)
        verbose_name = "HowTo"
        verbose_name_plural = "HowTo"


class Streamer(models.Model):
    orderPP = models.IntegerField('Номер ПП', default=10)
    name = models.CharField('ФИО', max_length=255, blank=False, null=True)
    nickName = models.CharField('Ник', max_length=255, blank=False, null=True, db_index=True)
    photo = models.ImageField('Фото)', upload_to='speaker_img/', blank=False, null=True)
    pageHeader = models.ImageField('Изображение для шапки страницы', upload_to='speaker_img/', blank=False, null=True)
    nickNameSlug = models.CharField(max_length=255, blank=True, null=True, unique=True, db_index=True, editable=False)
    linkVK = models.CharField('Ссылка на VK', max_length=255, blank=True, null=True )
    linkTW = models.CharField('Ссылка на Twitch', max_length=255, blank=True, null=True )
    linkYT = models.CharField('Ссылка на YouTube', max_length=255, blank=True, null=True )
    linkIN = models.CharField('Ссылка на Instagram', max_length=255, blank=True, null=True)
    views = models.IntegerField('Просмотров профиля', default=0)
    about = RichTextUploadingField('Описание', blank=True, null=True)
    streaming = RichTextUploadingField('Что стримит', blank=True, null=True)
    isAtHome = models.BooleanField('Отображать на главной?', default=False)
    uniqUrl = models.CharField('Хеш для ссылки (/star/stats/)', max_length=100,  blank=True,null=True, editable=False)

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


class Ticket(models.Model):
    price = models.IntegerField('Цена', blank=False, null=True)
    is_one_day = models.BooleanField('На один день?', default=False)
    is_two_day = models.BooleanField('На два дня?', default=False)

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
    t_id = models.CharField(max_length=255, blank=True, null=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Билет')
    streamer = models.ForeignKey(Streamer, on_delete=models.CASCADE, null=True, blank=True, verbose_name='От кого')
    quantity = models.IntegerField('Количество', default=1)

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
    session = models.CharField('Сессия', max_length=255, blank=True, null=True)
    tickets = models.ManyToManyField(CartItem, blank=True, verbose_name='Билеты')
    total_price = models.IntegerField('Стоимось корзины', default=0)

    def __str__(self):
        return f'Стоимость корзины : {self.total_price}'

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"