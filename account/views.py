from customer.models import Customer
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password
from django.http import Http404
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from vendor.models import Vendor

from .models import User
from .serializers import UserVerifySerializer, UserListSerializer, UserUpdateSerializer
from .token import user_tokenizer


class LogoutUser(APIView):

    def get(self, request, *args, **kwarg):
        context = {
            "Message": "Are you sure you want Logout?"
        }
        return Response(context)

    def post(self, request, *args, **kwarg):
        logout(request)
        context = {
            "Message": "'{}'Thank you, you have successfully logged out.".format(request.user)
        }
        return Response(context)


class UserList(generics.GenericAPIView):

    serializer_class = UserListSerializer

    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        serializer_context = {
            'request': request,
        }
        users_serializer = UserListSerializer(users, context=serializer_context, many=True)
        users_data = users_serializer.data
        context = {
            'Users': users_data,
        }
        return Response(context)

    def post(self, request, *args, **kwargs):
        new_user = UserListSerializer(data=request.data)
        if new_user.is_valid(raise_exception=True):
            new_user_saved = new_user.save()
            return Response({
                'Success': "'{}' has been successfully registered".format(new_user_saved.email)
            })
        return Response({
            'Failed': "Invalid information"
        })


class UserDetail(generics.GenericAPIView):

    serializer_class = UserUpdateSerializer

    def get_object(self, pk):
        try:
            user = User.objects.get(pk=pk)
            return user
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        user_serializer = UserUpdateSerializer(user,)
        user_data = user_serializer.data
        return Response(user_data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        user = self.get_object(pk)
        user_serializer = UserUpdateSerializer(user)
        if user_serializer.is_valid(raise_exception=True):
            user_serializer.save()
            return Response(user_serializer.data,status=status.HTTP_200_OK )
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ActivateUserView(generics.GenericAPIView):
    serializer_class = UserVerifySerializer

    def get_object(self,user_id):
        try:
            user_id = force_text(urlsafe_base64_decode(user_id))
            user = User.objects.get(pk=user_id)
            return user
        except User.DoesNotExist:
            raise Http404

    def get(self,request, user_id,token):
        user = self.get_object(user_id)
        validated = user_tokenizer.check_token(user, token)
        if validated:
            context = {
                "Message": "User Valid, Please set your Password"
            }
            return Response(context)
        context = {
            "Message": "User Invalid, Make sure to register first"
        }
        return Response(context)

    def put(self, request, user_id,token):
        user = self.get_object(user_id)
        validated = user_tokenizer.check_token(user, token)
        if validated:
            my_user = UserVerifySerializer(user, data=request.data, partial=True)
            if my_user.is_valid(raise_exception=True):
                password = my_user.validated_data.pop('password')
                password1 = my_user.validated_data.pop('confirm_password')
                if password == password1:
                    user_password = make_password(password)
                    my_user = my_user.save(password=user_password, is_active=True)
                    if user.user_type == 'VENDOR':
                        vendor = Vendor.objects.get(email=user.email)
                        vendor.user = user
                        vendor.save()
                    elif user.user_type == 'CUSTOMER':
                        customer = Customer.objects.get(email=user.email)
                        customer.user = user
                        customer.save()
                    context = {
                        "Message": f"'{my_user}' is Valid, Password Set Successfully"
                    }
                    return Response(context)
                else:
                    context = {
                        "Message": "Password Does Not match"
                    }
                    return Response(context)
            context = {
                "Message": "Unknown Error Occur"
            }
            return Response(context)
        context = {
            "Message": "Invalid Validation"
        }
        return Response(context)