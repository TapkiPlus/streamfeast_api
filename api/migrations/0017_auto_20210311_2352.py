# Generated by Django 3.1.5 on 2021-03-11 20:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_auto_20210311_2012'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Ticket',
            new_name='TicketType',
        ),
    ]
