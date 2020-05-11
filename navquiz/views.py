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
from .models import NavQuestion, NavAnswer

#from .forms import NavQuizStartForm

class StartNavQuiz(LoginRequiredMixin, generic.TemplateView):
    template_name = 'navQuiz/startNavQuiz.html'
    login_url = '/account/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        context = {'username':request.user}
        return render(request, self.template_name,
                      {'username':request.user})

    def post(self, request, *args, **kwargs):
        # initialize attempt
        attempt = NavQuizAttempt.objects.create(user=request.user,
                                        finish_time=timezone.now(),
                                        score=0,
                                        user_attempt_no=0)#user_attempt_no)
        # get next attempt no
        attempt.user_attempt_no=attempt.get_next_user_attempt_no()
        attempt.save()

        # Generate 5 questions to the Navquiz (defined in model function)
        attempt.generate_navQuiz()

        # Identify the next question
        next_question_attempt=attempt.getNextQuestionAttempt()

        # set the time for starting the new question
        attempt.startNextQuestionAttempt()

        return HttpResponseRedirect(
            reverse('navquiz:question',kwargs=
                    {'user_attempt':attempt.user_attempt_no,
                     'question_id':next_question_attempt.question.id}))
    # Need to update the Quesion_id?  Some randomization????

class QuestionView(LoginRequiredMixin, generic.CreateView):
    form_class = QuestionForm
    model = NavAnswersSubmitted
    login_url = '/account/login/'
    redirect_field_name = 'redirect_to'
    template_name='navQuiz/question.html'

    def get(self, request, *args, **kwargs):
        user_attempt_no = self.kwargs.pop('user_attempt')
        question_id = self.kwargs.pop('question_id')
        attempt = NavQuizAttempt.objects.get(user=request.user,
                                             user_attempt_no=user_attempt_no)
        question = NavQuestion.objects.get(id=question_id)
        question_attempt = NavAnswersSubmitted.objects.get(attempt=attempt,
                                                           question=question)
        form = self.form_class(request.GET or None)
        progress=attempt.progress()
        return render(request, self.template_name,
                      {'question':question, 'form':form,'progress':progress,
                       'username':request.user,'attempt':attempt,
                       'question_attempt':question_attempt})

    def post(self, request, *args, **kwargs):
        user_attempt_no = self.kwargs.pop('user_attempt')
        question_id = self.kwargs.pop('question_id')
        attempt = NavQuizAttempt.objects.get(user=request.user,
                                             user_attempt_no=user_attempt_no)
        question = NavQuestion.objects.get(id=question_id)
        question_attempt = NavAnswersSubmitted.objects.get(attempt=attempt, question=question)

        form = self.form_class(request.POST or None, instance=question)
        if attempt.submitted_bool==False:
            if form.is_valid():
                answer = form.cleaned_data['article_submitted']
                # Save user answer & process
                question_attempt.save_user_answer(answer)

                # if there is an unanswered question
                if attempt.isThereUnAnsweredQuestion():
                    # Identify the next question
                    next_question_attempt=attempt.getNextQuestionAttempt()

                    # set the time for starting the new question
                    attempt.startNextQuestionAttempt()

                    return HttpResponseRedirect(
                        reverse('navquiz:question',
                            kwargs={'user_attempt':attempt.user_attempt_no,
                        'question_id':next_question_attempt.question.id}))
                # if there is NOT another question (finish the navQuiz)
                else:
                    attempt.finishAttempt()
                    return HttpResponseRedirect(reverse('navquiz:endQuiz'
                        ,kwargs={'user_attempt':attempt.user_attempt_no}))
            else:
                raise Http404
        else:
            return HttpResponseRedirect(reverse('navquiz:endQuiz',
                        kwargs={'user_attempt':attempt.user_attempt_no}))


class EndOfQuizView(LoginRequiredMixin, generic.TemplateView):
    login_url = '/account/login/'
    redirect_field_name = 'redirect_to'
    template_name='navQuiz/endQuiz.html'

    def get(self, request, *args, **kwargs):
        user_attempt_no = self.kwargs.pop('user_attempt')
        attempt = NavQuizAttempt.objects.get(user=request.user,
                                             user_attempt_no=user_attempt_no)
        question_attempts=NavAnswersSubmitted.objects.filter(attempt=attempt)

        questions=NavQuestion.objects.filter(navanswerssubmitted__in=question_attempts)
        correct_answers = NavAnswer.objects.filter(question__in=questions)

        return render(request, self.template_name, {'attempt':attempt,
                                    'score':attempt.score,
                                    'question_attempts':question_attempts,
                                    'correct_answers':correct_answers,
                                    'username':request.user})


