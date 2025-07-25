from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from whatsappAPI.views import webhookviews
from ICCapiservices.api import ninja_api


urlpatterns = [
    path('admin/', admin.site.urls),
    path('webhook/', webhookviews.whatsapp_webhook, name='webhook'),
    path('api/', ninja_api.urls),

]

if settings.DEBUG_ENV:
  urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

admin.site.site_header='ICC Backend'
admin.site.index_title='Site Administration'
