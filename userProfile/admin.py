from django.contrib import admin

# Register your models here.
from userProfile.models import NavQuizAttempt, NavAnswersSubmitted
admin.site.register(NavQuizAttempt)
admin.site.register(NavAnswersSubmitted)

