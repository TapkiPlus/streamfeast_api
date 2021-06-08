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

class ActivityStreamerInline(admin.TabularInline):
    model = Activity.streamers.through
    verbose_name = "Guest"
    verbose_name_plural = "Guests"
    readonly_fields = ['nickName', 'name', 'isActive']
    # ordering = ("nickName",)

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
admin.site.register(Activity, ActivityAdmin)
# admin.site.register(OrderItem)
admin.site.register(SocialIcon)
