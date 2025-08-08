from django.contrib import admin
from tasks.models import Category, Event
# Register your models here.

admin.site.register(Category)
admin.site.register(Event)