from django.core.mail import send_mail, send_mass_mail
from django.dispatch import receiver

from order.signals import new_order_notification
from account.signals import new_user_create
from fva_project.settings import EMAIL_HOST_USER

from order.signals import update_order_notification

from order.models import Order


@receiver(new_order_notification)
def new_order_email(sender, **kwargs):
    order_info = {
        'customer': kwargs['customer'],
        'vendor': kwargs['vendor'],
        'order_status': kwargs['order_status'],
        'order': kwargs['order'],
    }

    order = Order.objects.get(pk=order_info['order'])
    customer_email = order.customer.email
    vendor_email = order.vendor.email

    message1 = f"Your Order {order}'s " \
               f"has been received. Kindly make payment." \
               f" Order status changed to " \
               f"'{order.order_status}'"
    message2 = f"Order {order}'s" \
               f"has been Initiated." \
               f" Order status changed to " \
               f"'{order.order_status}'"

    email_messages = (
        ('VGG FOOD VENDOR APP: Order Initiation', message1, EMAIL_HOST_USER, [customer_email]),
        ('VGG FOOD VENDOR APP: Order Initiation', message2, EMAIL_HOST_USER, [vendor_email]),
    )
    send_mass_mail(email_messages)


@receiver(update_order_notification)
def order_mod_email(sender, **kwargs):
    order = kwargs['order']

    order_info = {
        'customer': order.customer.pk,
        'vendor': order.vendor.pk,
        'order_status': order.order_status,
        'order': order.pk
    }

    message = f"Your Order {order}'s status has been changed to {order_info['order_status']}"
    vendor_email = order.vendor.email
    customer_email = order.customer.email
    print('Order Updated')
    send_mail(
        'VGG FOOD VENDOR APP: Order Update',
        message,
        EMAIL_HOST_USER,
        [customer_email, vendor_email],
        fail_silently=False,
    )


@receiver(new_user_create)
def new_user_email(sender, **kwargs):

    new_user = {
        'email': kwargs['email'],
        'message': kwargs['message'],
        'token': kwargs['token'],
        'user_id': kwargs['user_id'],
    }

    send_mail(
        'VGG FOOD VENDOR APP: Email Confirmation',
        new_user['message'],
        EMAIL_HOST_USER,
        [new_user['email']],
        fail_silently=False,
    )