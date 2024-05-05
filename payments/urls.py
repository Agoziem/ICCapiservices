from django.urls import path
from .views import *

urlpatterns = [
    path('payments/<int:organization_id>/', get_payments),
    path('payment/<int:payment_id>/', get_payment),
    path('addpayment/<int:organization_id>/', add_payment),
    path('updatepayment/<int:payment_id>/', update_payment),
    path('deletepayment/<int:payment_id>/', delete_payment),

    path('paymentsuccessful/<int:payment_id>/', payment_successful),
    path('paymentfailed/<int:payment_id>/', payment_failed),
]