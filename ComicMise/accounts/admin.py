from django.contrib import admin
from .models import Account, Address , Profile
# Register your models here.

admin.site.register(Account)
admin.site.register(Address)
admin.site.register(Profile)