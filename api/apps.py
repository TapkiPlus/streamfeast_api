import logging
from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler



class ApiConfig(AppConfig):
    name = 'api'

    STARTED = False

    def ready(self):
        if not STARTED:
            STARTED = True  
            from .email_client import send_oldest
            logging.basicConfig()
            logging.getLogger('apscheduler').setLevel(logging.WARNING)
            scheduler = BackgroundScheduler()
            scheduler.add_job(send_oldest, 'interval', seconds=10)
            scheduler.start()