from django.urls import path
from .views import *

urlpatterns = [
    path('payments/<int:organization_id>/', get_payments),
    path('payment/<int:payment_id>/', get_payment),
    path('payment/reference/<str:reference>/', get_payment_by_reference),
    path('paymentsbyuser/<int:user_id>/', get_payments_by_user), # new
    path('addpayment/<int:organization_id>/', add_payment),
    path('verifypayment/', verify_payment),
    path('updatepayment/<int:payment_id>/', update_payment),
    path('deletepayment/<int:payment_id>/', delete_payment),
    path('getorderreport/<int:organization_id>/', get_payment_count),
]