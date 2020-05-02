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
        start_time = datetime.now()
        finish_time=datetime(2000, 1, 1, 0, 0, 0, 0) # default placeholder
        score=0 #default placeholder

        #calculate last user_attempt_no
        if NavQuizAttempt.objects.filter(user=request.user):
            navquiz_attempts=NavQuizAttempt.objects.filter(user=request.user)
            navquiz_attempt = NavQuizAttempt.objects.latest('start_time')

            # iterate to the next user_attempt_no
            user_attempt_no = navquiz_attempt.user_attempt_no + 1
        else:
            user_attempt_no = 1
        attempt = NavQuizAttempt.objects.create(user=request.user,
                                        finish_time=finish_time,
                                        score=score,
                                        user_attempt_no=user_attempt_no)

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
                start_time=start_time,
                finish_time=finish_time)

        # ensure that the next_question is the first of the attempts.
        question_attempts=NavAnswersSubmitted.objects.filter(attempt=attempt)
        first_question_attempt = question_attempts.first()
        first_question = first_question_attempt.question

        return HttpResponseRedirect(
            reverse('navquiz:question',kwargs=
                    {'user_attempt':attempt.user_attempt_no,
                     'question_id':first_question.id}))
    # Need to update the Quesion_id?  Some randomization????

class QuestionView(LoginRequiredMixin, generic.CreateView):
    form_class = QuestionForm
    model = NavAnswersSubmitted
    login_url = '/account/login/'
    redirect_field_name = 'redirect_to'
    template_name='navQuiz/question.html'

    def calculateProgress(self, user, quiz_questions, attempt):
        answered_questions=NavAnswersSubmitted.objects.filter(user=user).filter(attempt=attempt).filter(submitted_bool=True).aggregate(Count('question'))
        total_questions=quiz_questions.aggregate(Count('id'))
        num_total_questions=total_questions.get('id__count')
        num_answered_questions=answered_questions.get('question__count')
        progress = num_answered_questions / num_total_questions * 100
        return progress

    def get(self, request, *args, **kwargs):
        user_attempt_no = self.kwargs.pop('user_attempt')
        question_id = self.kwargs.pop('question_id')
        attempt = NavQuizAttempt.objects.get(user=request.user,
                                             user_attempt_no=user_attempt_no)
        question = NavQuestion.objects.get(id=question_id)
        quiz_questions = NavAnswersSubmitted.objects.filter(attempt=attempt)
        question_attempt = NavAnswersSubmitted.objects.get(attempt=attempt,
                                                           question=question)
        form = self.form_class(request.GET or None)
        progress=self.calculateProgress(request.user,quiz_questions, attempt)

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

        question = question_attempt.question
        form = self.form_class(request.POST or None, instance=question)
        if attempt.submitted_bool==False:
            if form.is_valid():
                answer = form.cleaned_data['article_submitted']
                
                question_attempt.article_submitted=answer
                question_attempt.finish_time=timezone.now()
                print("super ", question_attempt.submitted_bool)
                question_attempt.submitted_bool=True
                question_attempt.save()
                question_attempt.time_taken=(question_attempt.finish_time - question_attempt.start_time)
                print("super ", question_attempt.submitted_bool)

                answer = NavAnswer.objects.get(question=question)
                #from decimal import *
                
                if answer.mpep_location== question_attempt.article_submitted:
                    question_attempt.correct_bool=True
                    question_attempt.save()
                else:
                    question_attempt.correct_bool=False
                    question_attempt.save()
                
                # Identify the next question I am not a huge fan
                next_question_attempt_id = question_attempt.id + 1
                if NavAnswersSubmitted.objects.filter(id=next_question_attempt_id).exists():
                    next_question_attempt= NavAnswersSubmitted.objects.get(id=next_question_attempt_id)
                        
                    next_question=next_question_attempt.question
                    print("potatoes  ", next_question_attempt.start_time)
                    next_question_attempt.start_time = timezone.now()
                    next_question_attempt.save()
                    print("sorry buddy ", next_question_attempt.start_time)
                    return HttpResponseRedirect(
                        reverse('navquiz:question',
                            kwargs={'user_attempt':attempt.user_attempt_no,
                                    'question_id':next_question.id}))
                else:

                    attempt.submitted_bool=True
                    attempt.finish_time=timezone.now()
                    attempt.save()
                        
                    attempt.time_taken=attempt.finish_time-attempt.start_time
                    attempt.save()

                    correct_answers = NavAnswersSubmitted.objects.filter(attempt=attempt, correct_bool=True)
                    wrong_answers = NavAnswersSubmitted.objects.filter(attempt=attempt, correct_bool=False)
                    correct_count = correct_answers.count()
                    wrong_count = wrong_answers.count()

                    attempt.score = 100 * correct_count / (correct_count + wrong_count)
                    attempt.save()
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


    # Create your views here.
