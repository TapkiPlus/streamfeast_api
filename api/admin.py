from django.contrib import admin
from .models import *


class SocialLinkInline (admin.TabularInline):
    model = SocialLink
    extra = 0
    ordering = ("id",)


class StreamerAdmin(admin.ModelAdmin):
    list_display = ['orderPP',
                    'nickName',
                    'name',
                    'isAtHome',
                    'isActive']
    list_filter = ('isAtHome',
                   'isActive')
    search_fields = ('nickName',
                     'name')
    list_display_links = ('nickName',
                          'name',
                          'isAtHome',
                          'isActive')
    inlines = [SocialLinkInline]

    class Meta:
        model = Streamer

admin.site.register(Subscribe)
admin.site.register(Streamer, StreamerAdmin)
admin.site.register(Faq)
admin.site.register(HowTo)
admin.site.register(TicketType)
admin.site.register(Ticket)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(PlatronPayment)
# admin.site.register(OrderItem)
admin.site.register(SocialIcon)

