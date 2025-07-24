from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from whatsappAPI.views import webhookviews
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import re_path

schema_view = get_schema_view(
    openapi.Info(
        title="ICC API",
        default_version='v1',
        description="API documentation for ICC services",
        terms_of_service="https://www.innovationscybercafe.com/terms-of-use/",
        contact=openapi.Contact(email="support@innovationscybercafe.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('webhook/', webhookviews.whatsapp_webhook, name='webhook'),
    path('api/', include('ICCapp.urls')),
    path('emailsapi/', include('emails.urls')),
    path('blogsapi/', include('blog.urls')),
    path('authapi/', include('authentication.urls')),
    path('customersapi/', include('customers.urls')),
    path('paymentsapi/', include('payments.urls')),
    path('servicesapi/', include('services.urls')),
    path('CBTapi/', include('CBTpractice.urls')),
    path('productsapi/', include('products.urls')),
    path('vidoesapi/', include('vidoes.urls')),
    path('whatsappAPI/', include('whatsappAPI.urls')),
    path('chatroomapi/', include('chatroom.urls')),
    path('notificationsapi/', include('notifications.urls')),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG_ENV:
  urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

admin.site.site_header='ICC Backend'
admin.site.index_title='Site Administration'
