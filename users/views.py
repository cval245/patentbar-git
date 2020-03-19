from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from users.forms import CustomUserCreationForm

from userProfile.models import QuizAttempt
# Create your views here.

class DashboardView(LoginRequiredMixin, View):
    login_url = 'login/'
    redirect_field_name = 'next'
    template_name = 'registration/dashboard.html'

    def get(self, request, *args, **kwargs):
        username = request.user
        return render(request, self.template_name, {'username': username})


class SignUpView(FormView):
    template_name = 'registration/signup.html'
    form_class = CustomUserCreationForm
    success_url = '/account/'

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url())

class ResultsView(LoginRequiredMixin, TemplateView):
    login_url = 'login/'
    redirect_field_name = 'next'
    template_name = 'users/results.html'

    def get(self, request, *args, **kwargs):
        username = request.user
        quizResults = QuizAttempt.objects.filter(user=request.user)
        #quizResults.annotate(Count('finish_time'))

        from django.db.models import Avg, Count, Min, Sum
        bob = QuizAttempt.objects.annotate(Count('finish_time')).values()
        print(bob)
        return render(request, self.template_name,
                      {'username':username, 'quizResults':quizResults})

    def days_hours_minutes_seconds(self, time):
        days = time.days
        hours = time.seconds//3600
        minutes = (time.seconds//60)%60
        seconds = time.seconds%60
        return {'days':days, 'hours':hours, 'minutes':minutes,
                'seconds':seconds}
