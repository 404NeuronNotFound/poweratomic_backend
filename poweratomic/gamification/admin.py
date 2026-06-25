from django.contrib import admin

from .models import UserBadge, UserXP

admin.site.register(UserXP)
admin.site.register(UserBadge)