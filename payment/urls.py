from django.urls import path

from .views import PaymentList,OrderPaymentViewset

urlpatterns = [
    path('', PaymentList.as_view(), name = 'order_payment_list'),
    path('detail/<pk>', OrderPaymentViewset.as_view(), name = 'order_payment'),

]