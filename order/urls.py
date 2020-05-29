from django.urls import path

from .views import (
    OrderListView,
    OrderDetailView,
)

app_name = 'order'

urlpatterns = [
    path('',OrderListView.as_view(),name = 'order_list'),
    path('detail/<pk>',OrderDetailView.as_view(),name = 'order_detail'),
]