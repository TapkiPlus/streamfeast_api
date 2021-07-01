# Generated by Django 3.1.5 on 2021-06-19 01:47

import ckeditor_uploader.fields
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session', models.CharField(max_length=255, unique=True, verbose_name='Сессия')),
                ('total_price', models.IntegerField(default=0, verbose_name='Стоимось корзины')),
            ],
            options={
                'verbose_name': 'Корзина',
                'verbose_name_plural': 'Корзины',
            },
        ),
        migrations.CreateModel(
            name='Faq',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.IntegerField(default=100, verbose_name='№ П/П')),
                ('question', models.CharField(max_length=255, null=True, verbose_name='Вопрос')),
                ('answer', ckeditor_uploader.fields.RichTextUploadingField(max_length=255, null=True, verbose_name='Ответ')),
            ],
            options={
                'verbose_name': 'FAQ',
                'verbose_name_plural': 'FAQ',
                'ordering': ('order_number',),
            },
        ),
        migrations.CreateModel(
            name='HowTo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.IntegerField(default=100, verbose_name='№ П/П')),
                ('question', models.TextField(null=True, verbose_name='Вопрос')),
                ('answer', ckeditor_uploader.fields.RichTextUploadingField(null=True, verbose_name='Ответ')),
                ('icon', models.ImageField(null=True, upload_to='icons/', verbose_name='Иконка')),
                ('is_open_by_default', models.BooleanField(default=False, verbose_name='Открыто по умолчанию')),
            ],
            options={
                'verbose_name': 'Как стать участником',
                'verbose_name_plural': 'Как стать участником',
                'ordering': ('order_number',),
            },
        ),
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('email', models.EmailField(max_length=254, primary_key=True, serialize=False, verbose_name='E-mail')),
                ('quantity', models.PositiveSmallIntegerField(default=1, verbose_name='Количество')),
                ('invite_type', models.PositiveSmallIntegerField(choices=[(1, 'Regular One'), (2, 'Regular Two'), (3, 'Invite'), (4, 'Press'), (5, 'Bloger')], default=1, verbose_name='Тип приглашения')),
            ],
            options={
                'verbose_name': 'Приглашение',
                'verbose_name_plural': 'Приглашения',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.TextField(primary_key=True, serialize=False, verbose_name='ID')),
                ('session', models.CharField(max_length=255, verbose_name='Сессия')),
                ('firstname', models.CharField(blank=True, max_length=255, null=True, verbose_name='Имя')),
                ('lastname', models.CharField(blank=True, max_length=255, null=True, verbose_name='Фамилия')),
                ('email', models.CharField(max_length=255, verbose_name='Email')),
                ('phone', models.CharField(blank=True, max_length=255, null=True, verbose_name='Телефон')),
                ('when_paid', models.DateTimeField(null=True, verbose_name='Дата и время оплаты')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('amount', models.IntegerField(default=0, verbose_name='Стоимось')),
                ('payment_system', models.TextField(blank=True, editable=False, null=True, verbose_name='Платежная система')),
                ('card_pan', models.TextField(blank=True, editable=False, null=True, verbose_name='Номер карты')),
                ('failure_code', models.IntegerField(blank=True, editable=False, null=True, verbose_name='Код ошибки')),
                ('failure_desc', models.TextField(blank=True, editable=False, null=True, verbose_name='Описание ошибки')),
            ],
            options={
                'verbose_name': 'Заказ',
                'verbose_name_plural': 'Заказы',
            },
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True, verbose_name='Название')),
                ('level', models.PositiveSmallIntegerField(choices=[(1, 'One'), (2, 'Two'), (3, 'Three'), (4, 'Four'), (5, 'Five')], default=1, verbose_name='Уровень')),
            ],
            options={
                'verbose_name': 'Место',
                'verbose_name_plural': 'Места',
            },
        ),
        migrations.CreateModel(
            name='PlatronPayment',
            fields=[
                ('id', models.CharField(editable=False, max_length=32, primary_key=True, serialize=False, verbose_name='PaymentId')),
                ('status', models.BooleanField(editable=False, verbose_name='Status')),
                ('redirect_url', models.CharField(editable=False, max_length=255, unique=True, verbose_name='RedirectURL')),
            ],
            options={
                'verbose_name': 'Платеж',
                'verbose_name_plural': 'Платежи',
            },
        ),
        migrations.CreateModel(
            name='SocialIcon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True, verbose_name='Название сети')),
                ('icon', models.ImageField(null=True, upload_to='speaker_img/', verbose_name='Обложка')),
            ],
            options={
                'verbose_name': 'Иконка соц. сети',
                'verbose_name_plural': 'Иконки соц. сетей',
            },
        ),
        migrations.CreateModel(
            name='Streamer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orderPP', models.IntegerField(default=10, verbose_name='Номер ПП')),
                ('nickName', models.CharField(db_index=True, max_length=255, null=True, verbose_name='Ник')),
                ('name', models.CharField(max_length=255, null=True, verbose_name='Имя Фамилия')),
                ('email', models.CharField(blank=True, max_length=255, null=True, verbose_name='Email')),
                ('photo', models.ImageField(blank=True, null=True, upload_to='speaker_img/', verbose_name='Аватар')),
                ('pageHeader', models.ImageField(blank=True, null=True, upload_to='speaker_img/', verbose_name='Обложка')),
                ('nickNameSlug', models.CharField(blank=True, db_index=True, max_length=255, null=True, unique=True)),
                ('about', ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True, verbose_name='Описание')),
                ('streaming', ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True, verbose_name='Что стримит')),
                ('isAtHome', models.BooleanField(default=False, verbose_name='Отображать на главной?')),
                ('sells', models.BooleanField(default=True, verbose_name='Отображать блок билетов и подпись?')),
                ('isActive', models.BooleanField(default=False, verbose_name='Отображать?')),
                ('uniqUrl', models.TextField(default=uuid.uuid4, editable=False, verbose_name='Хеш для ссылки (/profile/)')),
            ],
            options={
                'verbose_name': 'Стример',
                'verbose_name_plural': 'Стримеры',
            },
        ),
        migrations.CreateModel(
            name='Subscribe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
            ],
            options={
                'verbose_name': 'Подписка',
                'verbose_name_plural': 'Подписки',
            },
        ),
        migrations.CreateModel(
            name='TicketType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.IntegerField(null=True, verbose_name='Цена')),
                ('days_qty', models.PositiveSmallIntegerField(choices=[(1, 'Regular One'), (2, 'Regular Two'), (3, 'Invite'), (4, 'Press'), (5, 'Bloger')], default=1, verbose_name='Тип билета')),
            ],
            options={
                'verbose_name': 'Тип билета',
                'verbose_name_plural': 'Типы билетов',
                'ordering': ('price',),
            },
        ),
        migrations.CreateModel(
            name='UserData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session', models.CharField(max_length=255, unique=True, verbose_name='Сессия')),
                ('firstname', models.CharField(blank=True, max_length=255, null=True, verbose_name='Имя')),
                ('lastname', models.CharField(blank=True, max_length=255, null=True, verbose_name='Фамилия')),
                ('email', models.CharField(blank=True, max_length=255, null=True, verbose_name='Email')),
                ('phone', models.CharField(blank=True, max_length=255, null=True, verbose_name='Телефон')),
                ('wentToCheckout', models.IntegerField(default=0, verbose_name='Количество переходов к оформлению билета')),
                ('returnedToShop', models.IntegerField(default=0, verbose_name='Количество переходов на покупку билета снова')),
                ('clickedPay', models.IntegerField(default=0, verbose_name='Количество нажатий на оплатить')),
                ('tryedToPayAgain', models.IntegerField(default=0, verbose_name='Количество нажатий попробовать еще раз')),
                ('clickedTechAssistance', models.IntegerField(default=0, verbose_name='Количество кликов на техпомощь')),
                ('successfulPayments', models.IntegerField(default=0, verbose_name='Количество успешных платежей')),
                ('failedPayments', models.IntegerField(default=0, verbose_name='Количество безуспешных платежей')),
            ],
            options={
                'verbose_name': 'Данные пользователя',
                'verbose_name_plural': 'Данные пользователей',
            },
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('ticket_id', models.TextField(editable=False, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket_uuid', models.UUIDField(default=uuid.uuid4, verbose_name='QR-code')),
                ('ticket_type', models.PositiveSmallIntegerField(choices=[(1, 'Regular One'), (2, 'Regular Two'), (3, 'Invite'), (4, 'Press'), (5, 'Bloger')], default=1, verbose_name='Тип билета')),
                ('price', models.IntegerField(null=True, verbose_name='Цена')),
                ('when_cleared', models.DateTimeField(null=True, verbose_name='Дата и время погашения')),
                ('when_sent', models.DateTimeField(null=True, verbose_name='Дата и время отправки')),
                ('send_attempts', models.SmallIntegerField(default=0, verbose_name='Количество попыток отправки')),
                ('checkin_count', models.SmallIntegerField(default=0, verbose_name='Успешных попыток прохода')),
                ('checkin_last', models.DateTimeField(null=True, verbose_name='Дата и время последнего входа')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='api.order', verbose_name='Заказ')),
                ('streamer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='api.streamer', verbose_name='От кого')),
            ],
            options={
                'verbose_name': 'Билет',
                'verbose_name_plural': 'Билеты',
            },
        ),
        migrations.CreateModel(
            name='SocialLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.CharField(blank=True, max_length=255, null=True, verbose_name='Ссылка')),
                ('icon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.socialicon', verbose_name='Иконка')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='links', to='api.streamer', verbose_name='Стример')),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket_type', models.PositiveSmallIntegerField(choices=[(1, 'Regular One'), (2, 'Regular Two'), (3, 'Invite'), (4, 'Press'), (5, 'Bloger')], verbose_name='Тип билета')),
                ('price', models.IntegerField(null=True, verbose_name='Цена')),
                ('quantity', models.IntegerField(default=1, verbose_name='Количество')),
                ('amount', models.IntegerField(default=0, verbose_name='Стоимось')),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.order')),
                ('streamer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='api.streamer', verbose_name='От кого')),
            ],
            options={
                'verbose_name': 'Позиция заказа',
                'verbose_name_plural': 'Позиции заказов',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0, verbose_name='Количество')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.cart', verbose_name='Корзина')),
                ('streamer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.streamer', verbose_name='От кого')),
                ('ticket_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.tickettype', verbose_name='Билет')),
            ],
            options={
                'verbose_name': 'Позиция корзины',
                'verbose_name_plural': 'Позиции в корзинах',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.IntegerField(default=0, verbose_name='Номер ПП')),
                ('day', models.PositiveSmallIntegerField(choices=[(1, 'First'), (2, 'Second'), (3, 'Both')], default=3, verbose_name='День')),
                ('start', models.CharField(max_length=16, verbose_name='Начало')),
                ('end', models.CharField(max_length=16, verbose_name='Окончание')),
                ('title', models.CharField(max_length=32, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Описание')),
                ('image', models.ImageField(upload_to='activity_images/', verbose_name='Картинка')),
                ('icon', models.ImageField(upload_to='activity_icons/', verbose_name='Иконка')),
                ('place', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='api.place', verbose_name='Место')),
                ('streamers', models.ManyToManyField(to='api.Streamer', verbose_name='Участник')),
            ],
            options={
                'verbose_name': 'Активность',
                'verbose_name_plural': 'Активности',
                'ordering': ('priority', 'start'),
            },
        ),
    ]
