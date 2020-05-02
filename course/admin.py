from django.contrib import admin

# Register your models here.

from course.models import Course, Module, Content
admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Content)

