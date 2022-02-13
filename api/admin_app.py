from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.urls import path


def admin_statistics_view(request):
    return render(request, 'admin/statistics.html', {
        'title': 'Statistics'
    })


class CustomAdminSite(admin.AdminSite):

    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        app_list += [
            {
                'name': 'Streamfest API',
                'app_label': 'streamfest_api',
                'models': [
                    {
                        'name': 'Statistics',
                        'object_name': 'statistics',
                        'admin_url': '/admin/statistics',
                        'view_only': True,
                    }
                ],
            }
        ]
        return app_list

    def get_urls(self):
        urls = super().get_urls()
        urls += [
            path('statistics/', admin_statistics_view, name='admin-statistics'),
        ]
        return urls
