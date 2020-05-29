from django.dispatch import Signal

new_user_creation = Signal(providing_args=["email","user_type",])
