from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.http import HttpResponseRedirect
from datetime import datetime
from django.utils import timezone
from django.urls import reverse
from django.http import Http404

#from random import randint
import random
from django.db.models import Count

from userProfile.models import NavQuizAttempt, NavAnswersSubmitted
from .forms import QuestionForm
from .models import NavQuestion

#from .forms import NavQuizStartForm

class StartNavQuiz(LoginRequiredMixin, generic.TemplateView):
    template_name = 'navQuiz/startNavQuiz.html'
    context_object_name = 'quiz'
    login_url = '/account/login/'
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        finish_time=datetime(2000, 1, 1, 0, 0, 0, 0) # default placeholder
        score=0 #default placeholder
        attempt = NavQuizAttempt.objects.create(user=request.user,
                                                   finish_time=finish_time,
                                                   score=score)

        next_question_id=1# update in due course to a randomization thingy
        # Need to make sure the same question is not asked twice in the same
        # attempt

        count = NavQuestion.objects.aggregate(count=Count('id'))['count']

        num_questions_in_exam = 5
        list_of_question_id = list()

        # Generate list of question ids
        list_of_question_id=random.sample(range(1, count+1),
                                          num_questions_in_exam)

        #create List of questions
        for question_id in list_of_question_id:
            next_question=NavQuestion.objects.get(id=question_id)
            next_question_attempt=NavAnswersSubmitted.objects.create(
                user=request.user,
                attempt=attempt,
                question=next_question,
                finish_time=finish_time)
            print('singing along ', next_question_attempt.id)


        # ensure that the next_question is the first of the attempts.
        question_attempts=NavAnswersSubmitted.objects.filter(attempt=attempt)
        first_question_attempt = question_attempts.first()
        first_question = first_question_attempt.question

        return HttpResponseRedirect(
            reverse('navquiz:question',kwargs={'attempt':attempt.id,
                                            'question_id':first_question.id}))
    # Need to update the Quesion_id?  Some randomization????

class QuestionView(LoginRequiredMixin, generic.CreateView):
    form_class = QuestionForm
    model = NavAnswersSubmitted
    login_url = '/account/login/'
    redirect_field_name = 'redirect_to'
    template_name='navQuiz/question.html'

    def get(self, request, *args, **kwargs):
        attempt_id = self.kwargs.pop('attempt')
        question_id = self.kwargs.pop('question_id')
        attempt = NavQuizAttempt.objects.get(id=attempt_id)
        question = NavQuestion.objects.get(id=question_id)

        form = self.form_class(request.GET or None)
        return render(request, self.template_name,
                      {'question':question, 'form':form})

    def post(self, request, *args, **kwargs):
        attempt_id = self.kwargs.pop('attempt')
        question_id = self.kwargs.pop('question_id')
        attempt = NavQuizAttempt.objects.get(id=attempt_id)
        question = NavQuestion.objects.get(id=question_id)
        question_attempt = NavAnswersSubmitted.objects.get(attempt=attempt, question=question)

        question = question_attempt.question
        form = self.form_class(request.POST or None, instance=question)

        if form.is_valid():
            answer = form.cleaned_data['article_submitted']

            question_attempt.article_submitted=answer
            #question_attempt.finish_time=datetime.now()
            question_attempt.finish_time=timezone.now()

            question_attempt.save()
            # Identify the next question I am not a huge fan, very hacky
            next_question_attempt_id = question_attempt.id + 1
            if NavAnswersSubmitted.objects.filter(id=next_question_attempt_id).exists():
                next_question_attempt= NavAnswersSubmitted.objects.get(id=next_question_attempt_id)

                next_question=next_question_attempt.question
                return HttpResponseRedirect(reverse('navquiz:question',
                                            kwargs={'attempt':attempt.id,
                                            'question_id':next_question.id}))
            else:
                attempt.finish_time=timezone.now()
                attempt.save()

                attempt.time_taken = attempt.finish_time-attempt.start_time
                attempt.save()

                attempt.score = 50
                return HttpResponseRedirect(reverse('navquiz:endQuiz',
                                        kwargs={'attempt':attempt.id}))
        else:
            raise Http404


class EndOfQuizView(LoginRequiredMixin, generic.TemplateView):
    login_url = '/account/login/'
    redirect_field_name = 'redirect_to'
    template_name='navQuiz/endQuiz.html'

    def get(self, request, *args, **kwargs):
        attempt_id = self.kwargs.pop('attempt')
        attempt = NavQuizAttempt.objects.get(id=attempt_id)
        question_attempts = NavAnswersSubmitted.objects.filter(attempt=attempt)

        time_taken = self.days_hours_minutes_seconds(attempt.time_taken)

        return render(request, self.template_name, {'time_taken':time_taken})

    def days_hours_minutes_seconds(self, time):
        days = time.days
        hours = time.seconds//3600
        minutes = (time.seconds//60)%60
        seconds = time.seconds%60
        return {'days':days, 'hours':hours, 'minutes':minutes,
                'seconds':seconds}

# Create your views here.
