from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Person, PersonalInfo

# Register your models here.
admin.site.register(Person)
admin.site.register(PersonalInfo)

