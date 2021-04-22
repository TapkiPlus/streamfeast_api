from django.contrib import admin

from .models import *


class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 0
    ordering = ("id",)


class StreamerAdmin(admin.ModelAdmin):
    list_display = ['orderPP', 'nickName', 'name', 'isAtHome', 'isActive']
    list_filter = ('isActive', 'isAtHome', 'sells', )
    search_fields = ('nickName', 'name')
    list_display_links = ('nickName', 'name', 'isAtHome', 'isActive')
    inlines = [SocialLinkInline]

    class Meta:
        model = Streamer


class UserDataAdmin(admin.ModelAdmin):
    list_display = ['firstname',
                    'lastname',
                    'email',
                    'phone',
                    'wentToCheckout',
                    'returnedToShop',
                    'clickedPay',
                    'tryedToPayAgain',
                    'clickedTechAssistance']
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
admin.site.register(Order)
admin.site.register(PlatronPayment)
admin.site.register(Place)
admin.site.register(Activity)
# admin.site.register(OrderItem)
admin.site.register(SocialIcon)
admin.site.register(PlatronPayment)
