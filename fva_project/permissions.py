from django.http import Http404
from rest_framework import permissions

from vendor.models import Vendor


class IsVendor(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.user_type == "VENDOR"

    def has_object_permission(self, request, view, obj):
        return request.user.user_type == "VENDOR"


class IsCustomer(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.user_type == "CUSTOMER"

    def has_object_permission(self, request, view, obj):
        return request.user.user_type == "CUSTOMER"


class IsOwnerCustomer(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.email == request.user.email


class IsOwnerVendor(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.email == request.user.email


class IsAdminUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_staff


class IsOrderOwnerCustomer(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.customer.email == request.user.email


class IsOrderOwnerVendor(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.vendor.email == request.user.email


class IsMenuOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        return obj.vendor_id.email == request.user.email


def method_permission_classes(classes):
    def decorator(func):
        def decorated_func(self, *args, **kwargs):
            self.permission_classes = classes
            # this call is needed for request permissions
            self.check_permissions(self.request)
            return func(self, *args, **kwargs)
        return decorated_func
    return decorator