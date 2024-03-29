from django.urls import path

from . import views

urlpatterns = [
    path('get_streamers', views.GetStreamers.as_view()),
    path('get_streamer', views.GetStreamer.as_view()),
    path('get_streamer_stats', views.GetStreamerStats.as_view()),
    path('get_faq_common', views.GetFaqCommon.as_view()),
    path('get_faq_participant', views.GetFaqParticipant.as_view()),
    path('get_ticket_types', views.GetTicketTypes.as_view()),
    path('get_cart', views.GetCart.as_view()),
    path('get_activity', views.GetActivity.as_view()),
    path('get_activities', views.GetActivities.as_view()),
    path('get_places', views.GetPlaces.as_view()),
    path('get_place', views.GetPlace.as_view()),
    path('get_qr', views.GetQr.as_view()),
    path('add_item', views.AddItem.as_view()),
    path('add_item_quantity', views.AddItemQuantity.as_view()),
    path('delete_item_quantity', views.DeleteItemQuantity.as_view()),
    path('delete_item', views.DeleteItem.as_view()),
    path('save_user_data', views.SaveUserData.as_view()),
    path('get_user_data', views.GetUserData.as_view()),
    path('create_order', views.CreateOrder.as_view()),
    path('get_ticket_type', views.GetTicketType.as_view()),
    path('ticket_clear', views.TicketClear.as_view()),
    path('subscribe_email', views.SubscribeEmail.as_view()),
    path('payment_result', views.PaymentResult.as_view()),
    path('checkin', views.Checkin.as_view()),
    path('stats/tickets', views.TicketChart.as_view()),
    path('stats/streamers', views.StreamerChart.as_view()),
    path('stats/streamers-export', views.StreamerChartExport.as_view()),
    path('stats/userdata-export', views.UserdataExport.as_view()),
]
