from django.contrib import admin

# Register your models here.
from check_phone.models import User, Price, Request

admin.site.register(User)
admin.site.register(Price)
admin.site.register(Request)