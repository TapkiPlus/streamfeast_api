from django.urls import path,include
from . import views

urlpatterns = [
    path('get_streamers', views.GetStreamers.as_view()),
    path('get_streamer', views.GetStreamer.as_view()),


]
