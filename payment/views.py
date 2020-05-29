from customer.models import Customer
from order.models import Order
from order.serializers import OrderSerializer3
from order.signals import update_order_notification
from rest_framework import generics
from rest_framework.response import Response

from .models import OrderPayment
from .serializers import OrderPaymentSerializer, OrderPaymentSerializer2
from fva_project.permissions import (
                            IsAdminUser,
                            IsOwnerVendor,
                            method_permission_classes,
                            IsCustomer,
                            IsVendor
                            )


class PaymentList(generics.GenericAPIView):

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OrderPaymentSerializer2
        elif self.request.method == 'POST':
            return OrderPaymentSerializer
        else:
            return OrderPaymentSerializer2

    @method_permission_classes((IsAdminUser,))
    def get(self, request, *args, **kwargs):
        payment = OrderPayment.objects.all()
        serializer = OrderPaymentSerializer2(payment, many=True)
        payment_data = serializer.data
        context = {
            'Payment': payment_data
        }
        return Response(context)

    @method_permission_classes((IsAdminUser | IsCustomer | IsVendor))
    def post(self, request, *args, **kwargs):
        payment_data = request.data
        serializer = OrderPaymentSerializer(data=payment_data)
        if serializer.is_valid(raise_exception=True):
            order = serializer.validated_data.get('order')
            order = Order.objects.get(pk=order.pk)
            order_amount = order.get_total_order_price
            customer = order.customer.email
            customer = Customer.objects.get(email=customer)

            order_payment_saved = serializer.save(
                order=order,
                customer=customer,
                order_amount=order_amount
                )
            the_order = {
                'order_status':"On Queue"
            }

            change_order_status = OrderSerializer3(order, data=the_order)
            if change_order_status.is_valid(raise_exception=True):
                order_update = change_order_status.save()
                update_order_notification.send(
                    sender=order_update,
                    order=order,
                )

            return Response({
                "Success": "You have successfully made Payment for the {} Order".format(order_payment_saved)
            })


class OrderPaymentViewset(generics.RetrieveUpdateDestroyAPIView):
    queryset = OrderPayment.objects.all()
    serializer_class = OrderPaymentSerializer2
    permission_classes = [IsAdminUser|IsOwnerVendor]
