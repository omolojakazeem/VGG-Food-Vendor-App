from .base import *

DEBUG = False

ALLOWED_HOSTS = ['vgg_fva.herokuapp.com', ]

MY_SERVER = ALLOWED_HOSTS[0]

import django_heroku

django_heroku.settings(locals())
