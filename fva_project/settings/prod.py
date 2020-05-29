import django_heroku

DEBUG = False

ALLOWED_HOSTS = ['vgg_fga.herokuapp.com',]

MY_SERVER = ALLOWED_HOSTS[0]

django_heroku.settings(locals())

