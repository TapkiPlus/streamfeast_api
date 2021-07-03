import functools
from clevercsv.write import writer
from clevercsv.wrappers import read_dicts
from io import TextIOWrapper

from django import forms
from django.urls import path
from django.contrib import admin
from django.shortcuts import render, redirect

from tempfile import NamedTemporaryFile
from .models import *


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()

class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        w = writer(response)

        w.writerow(field_names)
        for obj in queryset:
            row = w.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"

def create_orders(modeladmin, request, queryset):
    invites = Invitation.objects.filter(email__in=queryset)
    Order.create_by_invites(invites)
    modeladmin.message_user(request, "Заказы были успешно созданы.")
create_orders.short_description="Создать заказы по приглашениям"


class InvitationAdmin(admin.ModelAdmin, ExportCsvMixin):
    readonly_fields = ['sent_count']
    list_display = ['email', 'quantity', 'invite_type', 'sent_count']
    change_list_template = "admin/invitation_changelist.html"

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return self.readonly_fields + ('email')
        return self.readonly_fields

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def delete_queryset(self, request, queryset):
        new_queryset = queryset.filter(sent_count=0)
        super().delete_queryset(request, new_queryset)

    def import_csv(self, request):
        if request.method == "POST":
            csv_src = TextIOWrapper(request.FILES["csv_file"].file, encoding=request.encoding)
            tmp = NamedTemporaryFile()
            with open(tmp.name, 'w') as f: 
                for line in csv_src:
                    f.write(line)
            dicts = read_dicts(tmp.name)
            Invitation.import_from(dicts)
            tmp.close()
            self.message_user(request, "СSV файл импортирован!")
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "admin/csv_form.html", payload
        )

    actions = [create_orders]

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

# @admin.ModelAdmin.action(description='Перевыслать билеты по выбранному заказу')
def send_again(modeladmin, request, queryset):
    Ticket.objects.filter(order__in=queryset).update(when_sent=None, send_attempts=0)
send_again.short_description="Перевыслать билеты по выбранному заказу"

class ActivityStreamerInline(admin.TabularInline):
    model = Activity.streamers.through
    verbose_name = "Guest"
    verbose_name_plural = "Guests"

class ActivityAdmin(admin.ModelAdmin):
    inlines = [ ActivityStreamerInline, ]
    exclude = ('streamers',)
    list_display = ['title', 'priority', 'day', 'start', 'end', 'get_place', 'get_streamers']

    def get_streamers(self, obj):
        streamers = map(lambda s: s.nickName, obj.streamers.all())
        result = ", ".join(streamers)
        return result
    get_streamers.short_description = 'Участники'

    def get_place(self, obj): 
        return f"{obj.place.name} ({obj.place.level})"
    get_place.short_description = 'Место'

    class Meta:
        model = Activity

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
    actions = [send_again]

    class Meta:
        model = Order

class TicketAdmin(admin.ModelAdmin, ExportCsvMixin):
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



#disable delete globally
#admin.site.disable_action('delete_selected')
admin.site.register(Subscribe)
admin.site.register(Streamer, StreamerAdmin)
admin.site.register(Faq)
admin.site.register(HowTo)
admin.site.register(TicketType)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Cart)
admin.site.register(UserData, UserDataAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(PlatronPayment)
admin.site.register(Place, PlaceAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Invitation, InvitationAdmin)
admin.site.register(SocialIcon)
