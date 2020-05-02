from django.contrib import admin

# Register your models here.
from navquiz.models import NavQuestion, NavAnswer


admin.site.register(NavQuestion)
admin.site.register(NavAnswer)
