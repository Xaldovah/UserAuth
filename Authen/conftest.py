import os
import django
from django.conf import settings

os.environ['DJANGO_SETTINGS_MODULE'] = 'Authen.settings'
django.setup()
