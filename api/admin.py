from django.contrib import admin

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

    def get_days_qty(self, obj):
        return obj.order_item.ticket_type.days_qty
    get_days_qty.short_description = 'Дней'

    def get_price(self, obj):
        oi = obj.order_item
        return oi.amount / oi.quantity
    get_price.short_description = 'Цена'

    def get_name(self, obj):
        return obj.order.firstname
    get_name.short_description = 'Имя'

    def get_last_name(self, obj):
        return obj.order.lastname
    get_last_name.short_description = 'Фамилия'

    def get_email(self, obj):
        return obj.order.email
    get_email.short_description = 'Email'

    def get_phone(self, obj):
        return obj.order.phone
    get_phone.short_description = 'Телефон'

    def get_when_paid(self, obj):
        return obj.order.when_paid
    get_when_paid.short_description = 'Дата и время оплаты'

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


admin.site.register(Subscribe)
admin.site.register(Streamer, StreamerAdmin)
admin.site.register(Faq)
admin.site.register(HowTo)
admin.site.register(TicketType)
admin.site.register(Ticket)
admin.site.register(Cart)
#admin.site.register(CartItem)
admin.site.register(UserData, UserDataAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(PlatronPayment)
admin.site.register(Place)
admin.site.register(Activity)
# admin.site.register(OrderItem)
admin.site.register(SocialIcon)
