from django.urls import path
from django.contrib import admin
from django.shortcuts import render
from .models import *

class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 0
    ordering = ("id",)

class StreamerAdmin(admin.ModelAdmin):
    list_display = ['orderPP', 'nickName', 'name', 'email', 'isAtHome', 'isActive', 'uniqUrl']
    list_filter = ('isActive', 'isAtHome', 'sells', )
    search_fields = ('nickName', 'name', 'email')
    list_display_links = ('nickName', 'name', 'email', 'isAtHome', 'isActive')
    inlines = [SocialLinkInline]

    class Meta:
        model = Streamer

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    ordering = ("id",)

class ActivityStreamerInline(admin.TabularInline):
    model = Activity.streamers.through
    verbose_name = "Guest"
    verbose_name_plural = "Guests"

class ActivityAdmin(admin.ModelAdmin):
    inlines = [
        ActivityStreamerInline,
    ]
    exclude = ('streamers',)

class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "firstname",
        "lastname",
        "email",
        "phone",
        "when_paid",
        "created_at",
        "amount",
        "payment_system",
        "card_pan",
        "failure_code",
        "failure_desc"
    ]
    inlines = [OrderItemInline]

    class Meta:
        model = Order

class TicketAdmin(admin.ModelAdmin):
    list_display = [
        "ticket_id",
        "when_cleared",
        "get_streamer",
        "get_days_qty",
        "get_price",
        "get_name",
        "get_last_name",
        "get_email",
        "get_phone",
        "get_when_paid"
    ]

    def get_streamer(self, obj):
        streamer = obj.order_item.streamer
        return streamer.nickName if streamer else None
    get_streamer.short_description = 'От кого'
    get_streamer.admin_order_field = 'order_item__streamer__nickName'

    def get_days_qty(self, obj):
        return obj.order_item.ticket_type.days_qty
    get_days_qty.short_description = 'Дней'
    get_days_qty.admin_order_field = 'order_item__ticket_type__days_qty'

    def get_price(self, obj):
        oi = obj.order_item
        return oi.amount / oi.quantity
    get_price.short_description = 'Цена'

    def get_name(self, obj):
        return obj.order.firstname
    get_name.short_description = 'Имя'
    get_name.admin_order_field = 'order__firstname'

    def get_last_name(self, obj):
        return obj.order.lastname
    get_last_name.short_description = 'Фамилия'
    get_last_name.admin_order_field = 'order__lastname'

    def get_email(self, obj):
        return obj.order.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'order__email'

    def get_phone(self, obj):
        return obj.order.phone
    get_phone.short_description = 'Телефон'
    get_phone.admin_order_field = 'order__phone'

    def get_when_paid(self, obj):
        return obj.order.when_paid
    get_when_paid.short_description = 'Дата и время оплаты'
    get_when_paid.admin_order_field = 'order__when_paid'

    search_fields = [
        'ticket_id', 
        'order_item__streamer__nickName',
        'order__firstname',
        'order__lastname',
        'order__email',
        'order__phone'
    ]

    class Meta:
        model = Ticket

class UserDataAdmin(admin.ModelAdmin):
    list_display = ['firstname',
                    'lastname',
                    'email',
                    'phone',
                    'wentToCheckout',
                    'returnedToShop',
                    'clickedPay',
                    'tryedToPayAgain',
                    'clickedTechAssistance',
                    'successfulPayments',
                    'failedPayments']
    search_fields = ('firstname',
                     'lastname',
                     'email')

    class Meta:
        model = UserData

class PlaceAdmin(admin.ModelAdmin):
    list_display = [ 'id', 'name', 'level' ]

    class Meta:
        model = Place



admin.site.register(Subscribe)
admin.site.register(Streamer, StreamerAdmin)
admin.site.register(Faq)
admin.site.register(HowTo)
admin.site.register(TicketType)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Cart)
#admin.site.register(CartItem)
admin.site.register(UserData, UserDataAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(PlatronPayment)
admin.site.register(Place, PlaceAdmin)
admin.site.register(Activity, ActivityAdmin)
# admin.site.register(OrderItem)
admin.site.register(SocialIcon)
