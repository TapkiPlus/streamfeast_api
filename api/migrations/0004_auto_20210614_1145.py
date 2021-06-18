# Generated by Django 3.1.5 on 2021-06-14 11:45

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20210512_2119'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='end',
            field=models.CharField(max_length=16, verbose_name='Окончание'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='start',
            field=models.CharField(max_length=16, verbose_name='Начало'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='title',
            field=models.CharField(max_length=32, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='place',
            name='level',
            field=models.PositiveSmallIntegerField(choices=[(1, 'One'), (2, 'Two'), (3, 'Three'), (4, 'Four'), (5, 'Five')], default=1, verbose_name='Уровень'),
        ),
        migrations.AlterField(
            model_name='place',
            name='name',
            field=models.CharField(max_length=64, unique=True, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='streamer',
            name='uniqUrl',
            field=models.TextField(default=uuid.uuid4, editable=False, verbose_name='Хеш для ссылки (/profile/)'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='ticket_id',
            field=models.TextField(editable=False, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
