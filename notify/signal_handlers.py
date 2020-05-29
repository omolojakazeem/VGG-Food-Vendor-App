from django.conf.global_settings import EMAIL_HOST_USER
from django.core.mail import send_mail, send_mass_mail
from django.dispatch import receiver
from django.http import Http404

from order.signals import new_order_notification,update_order_notification

from .models import Notification
from .serializers import NotifySerializer


@receiver(new_order_notification)
def notify(sender, **kwargs):
    order_info = {
        'customer': kwargs['customer'],
        'vendor': kwargs['vendor'],
        'order_status': kwargs['order_status'],
        'order': kwargs['order'],
    }

    notification_serializer_data = NotifySerializer(data=order_info)
    if notification_serializer_data.is_valid(raise_exception=True):
        notification_serializer_data.save()


@receiver(update_order_notification)
def notify_update(sender, **kwargs):
    order = kwargs['order']
    notification = Notification.objects.get(order=order)

    order_info = {
        'customer': order.customer.pk,
        'vendor': order.vendor.pk,
        'order_status':order.order_status,
        'order': order.pk
    }

    notification_serializer_data = NotifySerializer(notification,data=order_info)
    if notification_serializer_data.is_valid(raise_exception=True):
        notification_serializer_data.save()

