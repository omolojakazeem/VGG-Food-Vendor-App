import random
import string

from customer.models import Customer
from django.http import Http404
from menu.models import Menu
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Order
from .serializers import (
    OrderMenuSerializer,
    OrderSerializer,
    MyOrderSerializer
)
from .signals import new_order_notification, update_order_notification
from fva_project.permissions import(
                            IsAdminUser,
                            method_permission_classes,
                            IsCustomer,
                            IsOrderOwnerCustomer,
                            IsOrderOwnerVendor
                            )


def get_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


class OrderListView(generics.GenericAPIView):

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderMenuSerializer
        elif self.request.method == 'GET':
            return OrderSerializer
        else:
            return OrderSerializer

    @method_permission_classes((IsAdminUser,))
    def get(self, request, *args, **kwargs):
        order = Order.objects.all()
        serializer_context = {
            'request':request,
        }

        serializer = OrderSerializer(order, context=serializer_context, many=True)
        order_data = serializer.data
        context = {
            'Orders': order_data
        }
        return Response(context)

    @method_permission_classes((IsCustomer,))
    def post(self, request, *args, **kwargs):
        order_menu_request_data = request.data
        order_menu_serializer = OrderMenuSerializer(data=order_menu_request_data, )
        if order_menu_serializer.is_valid(raise_exception=True):

            menu_id = order_menu_serializer.validated_data.get('menu')
            description = order_menu_serializer.validated_data.get('description')

            menu = Menu.objects.get(pk=menu_id.pk)
            vendor = menu.vendor_id
            customer = Customer.objects.get(user=request.user)

            order_menu_saved = order_menu_serializer.save(
                vendor=vendor,
                customer=customer,
                menu=menu, )

            if order_menu_saved:
                ref_code = get_ref_code()
                order_context = {
                    'customer': customer.pk,
                    'vendor': vendor.pk,
                    'description': description,
                    'order_ref': ref_code,
                }

                order_request_data = MyOrderSerializer(data=order_context, )
                if order_request_data.is_valid(raise_exception=True):
                    order_saved = order_request_data.save()
                    order_saved.order_items.add(order_menu_saved)

                    new_order_notification.send(
                        sender=order_saved,
                        customer=order_saved.customer.pk,
                        vendor=order_saved.vendor.pk,
                        order=order_saved.pk,
                        order_status=order_saved.order_status
                    )

                    return Response(order_request_data.data, status=status.HTTP_200_OK)
                return Response(order_request_data.errors, status=status.HTTP_400_BAD_REQUEST)

        context = {
            'Message': "Invalid Inputs",
        }
        return Response(context)


class OrderDetailView(generics.GenericAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser | IsOrderOwnerCustomer | IsOrderOwnerVendor]

    def get_object(self, pk):
        try:
            order = Order.objects.get(pk=pk)
            return order
        except Order.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        my_order = self.get_object(pk)
        order_serializer = OrderSerializer(my_order, many=False)
        return Response(order_serializer.data,status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        order_data = request.data
        my_order = self.get_object(pk)
        order_serializer = OrderSerializer(my_order, data=order_data)

        if order_serializer.is_valid():
            order = order_serializer.save()
            update_order_notification.send(
                sender=order,
                order=order,
            )
            return Response(order_serializer.data,status=status.HTTP_200_OK)
        return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        my_order = self.get_object(pk)
        my_order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

