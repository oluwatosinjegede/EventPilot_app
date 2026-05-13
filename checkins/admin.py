from django.contrib import admin
from .models import *
for model in list(globals().values()):
    if hasattr(model, '_meta') and getattr(model._meta, 'app_label', None) == 'checkins':
        try: admin.site.register(model)
        except admin.sites.AlreadyRegistered: pass