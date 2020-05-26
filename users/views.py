from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from users.forms import CustomUserCreationForm

from userProfile.models import QuizAttempt, NavQuizAttempt
from userProfile.models import CourseCompletion, ModuleCompletion
from quiz.models import Quiz
from datetime import timedelta
# Create your views here.

class DashboardView(LoginRequiredMixin, View):
    login_url = 'login/'
    redirect_field_name = 'next'
    template_name = 'registration/dashboard.html'

    def get(self, request, *args, **kwargs):
        high_attempt = NavQuizAttempt.objects.filter(user=request.user).order_by('-score').first()
        latest_attempt = NavQuizAttempt.objects.filter(user=request.user).order_by('-finish_time').first()

        completed_courses =CourseCompletion.objects.filter(user=request.user,
                                                        finished_bool=True)

        started_courses=CourseCompletion.objects.filter(user=request.user,
                                                        finished_bool=False)
        started_modules_course = ModuleCompletion.objects.filter(
            course_attempt__in=started_courses)
        started_modules_course=started_modules_course.filter(
            finished_bool=True)
        started_courses=CourseCompletion.objects.filter(
            modulecompletion__in=started_modules_course).distinct()
        print('started_courses = ', started_courses)

        return render(request, self.template_name,
                      {'username': request.user,
                       'high_attempt': high_attempt,
                       'latest_attempt':latest_attempt,
                       'completed_courses':completed_courses,
                       'started_courses':started_courses
        })


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

        # Get Quiz Results
        quizResults = QuizAttempt.objects.filter(user=request.user,
                                                 submitted_bool=True)
        latestQuizResults = quizResults.order_by('quiz','-finish_time').distinct('quiz')
        bestQuizResults = quizResults.order_by('quiz','-score').distinct('quiz')
        # Get NavQuiz Results
        NavQuizResults=NavQuizAttempt.objects.filter(user=request.user,
                                                    submitted_bool=True)
        latestNavQuizResult =NavQuizResults.order_by('-finish_time').first()
        bestNavQuizResult = NavQuizResults.order_by('-score').first()

        return render(request, self.template_name,
                      {'username':username,
                       'bestQuizResults':bestQuizResults,
                       'latestQuizResults':latestQuizResults,
                       'bestNavQuizResult':bestNavQuizResult,
                       'latestNavQuizResult':latestNavQuizResult})

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

class NavQuizResultsView(LoginRequiredMixin, TemplateView):
    login_url = 'login/'
    redirect_field_name = 'next'
    template_name = 'users/navQuizResults.html'

    def get(self, request, *args, **kwargs):
        username = request.user
        navQuizResults = NavQuizAttempt.objects.filter(user=request.user,
                                                       submitted_bool=True)
        navQuizResults = navQuizResults.order_by('-finish_time')

        return render(request, self.template_name,
                      {'username':username, 'navQuizResults':navQuizResults})
