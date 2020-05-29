from django.dispatch import receiver
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.response import Response

from account.serializers import UserCreateSerializer
from account.signals import new_user_create
from account.token import user_tokenizer
from customer.signals import new_user_creation
from fva_project.settings import MY_SERVER


@receiver(new_user_creation)
def received_from_users(sender, *args, **kwargs):
    user_info = {
        'email': kwargs['email'],
        'user_type': kwargs['user_type']
    }
    user = UserCreateSerializer(data=user_info, )
    if user.is_valid(raise_exception=True):
        email = kwargs['email']
        user_type = kwargs['user_type']
        new_user = user.save(is_active=False, user_type=user_type)

        user_id = urlsafe_base64_encode(force_bytes(new_user.pk))
        token = user_tokenizer.make_token(new_user)
        message = 'http://' + MY_SERVER + reverse('account:auth_user_reg',
                                                  kwargs={'user_id': user_id, 'token': token})
        new_user_create.send(
            sender=user,
            email=email,
            user_id=user_id,
            token=token,
            message=message
        )
        return Response("User Created Successfully. Kindly Check your email")
