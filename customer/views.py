from account.serializers import UserCreateSerializer
from account.token import user_tokenizer

from django.core.mail import send_mail
from django.http import Http404
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from fva_project.settings import EMAIL_HOST_USER, MY_SERVER

from rest_framework import status, generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Customer
from .serializers import CustomerSerializer
from .signals import new_user_creation
from fva_project.permissions import(
                                IsCustomer,
                                IsAdminUser,
                                method_permission_classes,
                                IsOwnerCustomer,
                                IsOwnerVendor,
                                IsVendor
                            )


class CustomerListViews(generics.GenericAPIView):

    serializer_class = CustomerSerializer

    @method_permission_classes((IsAdminUser,))
    def get(self, request, *args, **kwargs):
        customers = Customer.objects.all()
        serializer_context = {
            'request': request,
        }
        ser_customers = CustomerSerializer(customers, context=serializer_context, many=True)
        customers_data = ser_customers.data
        context = {
            'Customers': customers_data,
        }
        return Response(context)

    @method_permission_classes((AllowAny,))
    def post(self, request, *args, **kwargs):
        new_customer = CustomerSerializer(data=request.data)
        if new_customer.is_valid(raise_exception=True):
            customer_email = new_customer.validated_data.get('email')
            new_customer_saved = new_customer.save()
            new_user_creation.send(
                sender=new_customer_saved,
                email=customer_email,
                user_type="CUSTOMER"
            )
            return Response({
                'Success': "'{}' has been successfully registered".format(new_customer_saved.get_full_name)
            })
        return Response({
            'Failed': "Invalid information"
        })


class CustomerDetailView(generics.GenericAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [IsOwnerCustomer | IsAdminUser]

    def get_object(self, pk):
        try:
            customer = Customer.objects.get(pk=pk)
            return customer
        except Customer.DoesNotExist:
            raise Http404

    @method_permission_classes((IsAdminUser|IsVendor|IsOwnerCustomer))
    def get(self, request, pk, format=None):
        customer = self.get_object(pk)
        serializer_context = {
            'request': request,
        }
        cus_serializer = CustomerSerializer(customer, context=serializer_context)
        return Response(cus_serializer.data)

    @method_permission_classes((IsAdminUser|IsOwnerCustomer))
    def put(self, request, pk, format=None):
        customer = self.get_object(pk)
        cus_serializer = CustomerSerializer(customer, data=request.data)
        if cus_serializer.is_valid():
            cus_serializer.save()
            return Response(cus_serializer.data)
        return Response(cus_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @method_permission_classes((IsAdminUser | IsOwnerCustomer))
    def delete(self, request, pk, format=None):
        customer = self.get_object(pk)
        customer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
