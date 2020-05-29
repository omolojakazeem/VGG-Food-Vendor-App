from django.http import Http404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from vendor.models import Vendor

from .models import Menu
from .serializers import MenuUpdateSerializer, MenuListSerializer, MenuCreateSerializer
from fva_project.permissions import(
                            method_permission_classes,
                            IsVendor,
                            IsAdminUser,
                            IsMenuOwner
                            )


class MenuListView(generics.GenericAPIView):
    serializer_class = MenuCreateSerializer

    @method_permission_classes((AllowAny,))
    def get(self, request, *args, **kwargs):
        menu = Menu.objects.all()
        serializer = MenuCreateSerializer(menu, many=True)
        menu_data = serializer.data
        context = {
            'Menus': menu_data
        }
        return Response(context)

    @method_permission_classes((IsVendor,))
    def post(self, request, *args, **kwargs):
        menu_data = request.data
        serializer = MenuCreateSerializer(data=menu_data)
        if serializer.is_valid(raise_exception=True):
            vendor = Vendor.objects.get(user=request.user)
            menu_data_save = serializer.save(vendor_id=vendor)
            return Response({
                "Success": "You have successfully created the {} Menu".format(menu_data_save.name)
            })


class MenuDetailView(generics.GenericAPIView):

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return MenuUpdateSerializer
        elif self.request.method == 'GET':
            return MenuListSerializer
        else:
            return MenuListSerializer

    def get_object(self, pk):
        try:
            obj = Menu.objects.get(pk=pk, )
            self.check_object_permissions(self.request, obj)
            return obj
        except Menu.DoesNotExist:
            raise Http404

    @method_permission_classes((IsAuthenticated,))
    def get(self, request, pk, format=None):
        my_menu = self.get_object(pk)
        menu_serializer = MenuListSerializer(my_menu)
        return Response(menu_serializer.data, status=status.HTTP_200_OK)

    @method_permission_classes((IsMenuOwner | IsAdminUser,))
    def put(self, request, pk, format=None):
        menu_data = request.data
        my_menu = self.get_object(pk=pk)
        menu_serializer = MenuUpdateSerializer(my_menu,data=menu_data)

        if menu_serializer.is_valid():
            menu_serializer.save()
            return Response(menu_serializer.data,status=status.HTTP_200_OK)
        return Response(menu_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @method_permission_classes((IsMenuOwner | IsAdminUser,))
    def delete(self, request, pk, format=None):
        my_menu = self.get_object(pk=pk)
        my_menu.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
