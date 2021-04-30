import logging
from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler


class ApiConfig(AppConfig):
    name = 'api'

    def ready(self): 
        from .email_client import send_oldest
        scheduler = BackgroundScheduler()
        scheduler.add_job(send_oldest, 'interval', seconds=3)
        scheduler.start()