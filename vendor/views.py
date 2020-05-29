from account.models import User
from customer.signals import new_user_creation
from django.http import Http404
from menu.models import Menu
from rest_framework import status, generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Vendor
from .serializers import VendorSerializer
from fva_project.permissions import (
                            IsOwnerVendor,
                            IsCustomer,
                            IsAdminUser,
                            method_permission_classes
                            )


class VendorListView(generics.GenericAPIView):

    serializer_class = VendorSerializer

    @method_permission_classes((IsAdminUser,))
    def get(self, request, *args, **kwargs):

        vendors = Vendor.objects.all()
        serializer_context = {
            'request': request,
        }
        ser_vendors = VendorSerializer(vendors, context=serializer_context, many=True)
        vendors_data = ser_vendors.data
        context = {
            'Vendors': vendors_data,
        }

        return Response(context)

    @method_permission_classes((AllowAny,))
    def post(self, request, *args, **kwargs):
        new_vendor = VendorSerializer(data=request.data)
        if new_vendor.is_valid(raise_exception=True):
            vendor_email = new_vendor.validated_data.get('email')
            new_vendor_saved = new_vendor.save()
            new_user_creation.send(
                sender=new_vendor_saved,
                email=vendor_email,
                user_type="VENDOR"
            )
            return Response({
                'Success': "'{}' has been successfully registered".format(new_vendor_saved.business_name)
            })

        return Response({
            'Failed': "Invalid information"
        })


class VendorDetailView(generics.GenericAPIView):
    serializer_class = VendorSerializer

    def get_object(self, pk):
        try:
            vendor = Vendor.objects.get(pk=pk)
            return vendor
        except Vendor.DoesNotExist:
            raise Http404

    @method_permission_classes((IsAdminUser, IsCustomer))
    def get(self, request, pk, format=None):
        vendor = self.get_object(pk)
        serializer_context = {
            'request': request,
        }
        ven_serializer = VendorSerializer(vendor, context=serializer_context )
        return Response(ven_serializer.data)

    @method_permission_classes((IsAdminUser | IsOwnerVendor))
    def put(self, request, pk, format=None):
        vendor = self.get_object(pk)

        ven_serializer = VendorSerializer(vendor, data=request.data)
        if ven_serializer.is_valid():
            ven_serializer.save()
            return Response(ven_serializer.data)
        return Response(ven_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @method_permission_classes((IsAdminUser | IsOwnerVendor))
    def delete(self, request, pk, format=None):
        vendor = self.get_object(pk)
        vendor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VendorMenuListView(APIView):

    def get(self, request, *args, **kwargs):
        vendor = User.objects.get(user=self.request.user)
        menus = Menu.objects.filter(vendor_id=vendor)
        ser_menus = VendorSerializer(menus, many=True)
        menu_data = ser_menus.data
        context = {
            'My Menus': menu_data,
        }

        return Response(context)
