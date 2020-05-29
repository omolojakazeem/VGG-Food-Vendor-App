from django.dispatch import Signal

new_user_create= Signal(providing_args=["email", "user_id","token","message"])