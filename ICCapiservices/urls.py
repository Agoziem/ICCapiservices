"""ICCapiservices URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('ICCapp.urls')),
    path('emailsapi/', include('emails.urls')),
    path('blogsapi/', include('blog.urls')),
    path('authapi/', include('authentication.urls')),
    path('customersapi/', include('customers.urls')),
    path('paymentsapi/', include('payments.urls')),
    path('servicesapi/', include('services.urls')),
    path('CBTapi/', include('CBTpractice.urls')),
]

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

admin.site.site_header='ICC Backend'
admin.site.index_title='Site Administration'
