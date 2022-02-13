import logging
from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig
from apscheduler.schedulers.background import BackgroundScheduler

class AdminApiConfig(AdminConfig):
    default_site = 'api.admin_app.CustomAdminSite'


running = False

class ApiConfig(AppConfig):
    name = 'api'

    def ready(self):
        if not running: 
            running = True
            logging.warning("[+] Starting tasks executors")
            from .email_client import send_oldest
            scheduler = BackgroundScheduler()
            scheduler.add_job(send_oldest, 'interval', seconds=3)
            scheduler.start()
