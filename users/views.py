from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from users.forms import CustomUserCreationForm

from userProfile.models import QuizAttempt
from quiz.models import Quiz
from datetime import timedelta
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
        quizResults = QuizAttempt.objects.filter(user=request.user,
                                                 time_taken__gt=timedelta(microseconds=1))
        from django.db.models import Count
        latestQuizResults = quizResults.order_by('quiz','-finish_time').distinct('quiz')
        bestQuizResults = quizResults.order_by('quiz','-score').distinct('quiz')

        return render(request, self.template_name,
                      {'username':username,
                       'bestQuizResults':bestQuizResults,
                       'latestQuizResults':latestQuizResults})

class QuizResultsView(LoginRequiredMixin, TemplateView):
    login_url = 'login/'
    redirect_field_name = 'next'
    template_name = 'users/quizResults.html'

    def get(self, request, *args, **kwargs):
        username = request.user
        quiz_id = self.kwargs.pop('pk')
        quiz = Quiz.objects.get(id=quiz_id)
        quizResults = QuizAttempt.objects.filter(user=request.user,quiz=quiz,
                                                 time_taken__gt=timedelta(microseconds=1))
        quizResults = quizResults.order_by('-finish_time')


        return render(request, self.template_name,
                      {'username':username, 'quizResults':quizResults})

    
