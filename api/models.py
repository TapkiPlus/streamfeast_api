from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.db.models.signals import post_save
from pytils.translit import slugify
from random import choices
import string

class Streamer(models.Model):
    orderPP = models.IntegerField('Номер ПП', default=10)
    name = models.CharField('ФИО', max_length=255, blank=False, null=True)
    nickName = models.CharField('Ник', max_length=255, blank=False, null=True, db_index=True)
    photo = models.ImageField('Фото)', upload_to='speaker_img/',
                              blank=False, null=True)
    pageHeader = models.ImageField('Изображение для шапки страницы', upload_to='speaker_img/', blank=False,
                                    null=True)

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
        return 'Стример : {}'.format(self.name)

    class Meta:
        verbose_name = "Стример"
        verbose_name_plural = "Стримеры"