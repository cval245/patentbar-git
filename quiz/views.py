from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Value, BooleanField
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic

from .forms import  AnswerForm, QuizStartForm
from .models import Answer, Question, Quiz
from userProfile.models import AnswersSubmitted, QuizAttempt
from datetime import datetime
# Create your views here.

def HomePageView(request):
    template_name = 'homePage.html'
    return render(request, template_name)

class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'quiz/index.html'
    context_object_name = 'quiz'
    login_url = '/account/login/'
    redirect_field_name = 'redirect_to'

    def get_queryset(self):
        """Return all the quizzes"""
        return Quiz.objects.order_by('title')

class QuizDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'quiz/detail.html'
    model = Quiz
    form_class = QuizStartForm
    login_url = '/account/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        form = self.form_class(request.GET or None)
        return render(request, self.template_name, {'form':form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        finish_time=datetime(2000, 1, 1, 0, 0, 0, 0) # default placeholder
        score=0 #default placeholder
        if form.is_valid():
            quiz = form.cleaned_data['quizzes']
            submission = QuizAttempt.objects.create(user=request.user,
                                                    quiz=quiz,
                                                    finish_time=finish_time,
                                                    score=score)
            first_question=Question.objects.filter(quiz=quiz).first()
            return HttpResponseRedirect(
                reverse('quiz:question',
                        kwargs={'question_id':first_question.id,
                                'pk':quiz.id,
                                'attempt':submission.id}))
        return HttpResponseRedirect('/quiz/')


class QuestionView(LoginRequiredMixin, generic.CreateView):
    form_class = AnswerForm
    template_name = 'quiz/question.html'
    model = Question
    login_url = '/account/login/'
    redirect_field_name = 'redirect_to'

    def calculateProgress(self, user, quiz_questions, attempt):
        answered_questions=AnswersSubmitted.objects.filter(user=user).filter(attempt=attempt).aggregate(Count('question'))
        total_questions=quiz_questions.aggregate(Count('id'))
        num_total_questions=total_questions.get('id__count')
        num_answered_questions=answered_questions.get('question__count')
        progress = num_answered_questions / num_total_questions * 100
        return progress

    def get(self, request, *args, **kwargs):
        question_id = self.kwargs.pop('question_id')
        quiz_id = self.kwargs.pop('pk')
        quiz = Quiz.objects.get(id=quiz_id)
        quiz_questions=Question.objects.filter(quiz=quiz)
        attempt_id = self.kwargs.pop('attempt')
        attempt = QuizAttempt.objects.get(id=attempt_id)

        question = Question.objects.get(id=question_id)
        answer_selected = AnswersSubmitted.objects.filter(question=question,
                                                          attempt=attempt)
        # Determine if the next question is there, then move to it
        # After the final question is answered, does a passthrough to
        # look for unanswered questions. If there are none, it moves to
        # the submitquiz section
        results = AnswersSubmitted.objects.filter(question__in=quiz_questions,
                                                  attempt=attempt)
        answered_questions = results.values('question')
        unanswered_questions = quiz_questions.exclude(
            id__in=answered_questions)
        answered_questions=quiz_questions.filter(id__in=answered_questions)

        answered_questions = answered_questions.annotate(
            answered_bool=Value(True, BooleanField()))
        unanswered_questions = unanswered_questions.annotate(
            answered_bool=Value(False, BooleanField()))
        status_questions = answered_questions.union(unanswered_questions).order_by('id')
        # Prepopulates the form field, if the user already selected
        if answer_selected:
            answer_selected_id=answer_selected.get().answer.id
            form = self.form_class(request.GET or None, question=question_id,
                                   initial={'choice':answer_selected_id})

        else:
            form = self.form_class(request.GET or None, question=question_id)

        progress=self.calculateProgress(request.user, quiz_questions,attempt)
        return render(request, self.template_name,
                      {'form':form, 'question':question,
                       'status_questions':status_questions,
                       'quiz':quiz,
                       'answered_questions':answered_questions,
                       'attempt_id':attempt_id, 'progress':progress})

    def post(self, request, *args, **kwargs):
        question_id = self.kwargs.pop('question_id')
        quiz_id = self.kwargs.pop('pk')
        attempt_id = self.kwargs.pop('attempt')

        ATTEMPT = QuizAttempt.objects.get(id=attempt_id)
        next_question_id = question_id + 1
        quiz = Quiz.objects.get(id=quiz_id)
        quiz_questions=Question.objects.filter(quiz=quiz)
        QUESTION = quiz_questions.get(id=question_id)
        form = self.form_class(request.POST, question=question_id)

        if form.is_valid():
            ANSWER = form.cleaned_data['choice']

            if ATTEMPT.submitted_bool == False:

                # determine if user already entered an answer for that questions
                # if so, then update the old answer.
                if AnswersSubmitted.objects.filter(user=request.user,
                                                   question=QUESTION,
                                                   attempt=ATTEMPT).exists():
                    old_answer=AnswersSubmitted.objects.filter(user=request.user,
                                                               question=QUESTION,
                                                               attempt=ATTEMPT)
                    new_answer=old_answer.update(answer=ANSWER)
                else:
                    submission=AnswersSubmitted.objects.create(user=request.user,
                                                               question=QUESTION,
                                                               answer=ANSWER,
                                                               attempt=ATTEMPT)
            # Determine if the next question is there, then move to it
            # After the final question is answered, does a passthrough to
            # look for unanswered questions. If there are none, it moves to
            # the submitquiz section
            results = AnswersSubmitted.objects.filter(question__in=quiz_questions,
                                                      attempt=ATTEMPT)
            answered_questions = results.values('question')
            unanswered_questions = quiz_questions.exclude(id__in=answered_questions)

            if quiz_questions.filter(id=next_question_id):
                next_question=quiz_questions.get(id=next_question_id)
                return HttpResponseRedirect(
                    reverse('quiz:question',
                            kwargs={'question_id':next_question_id,
                                    'pk':quiz.id, 'attempt':attempt_id}))

            elif unanswered_questions.count() > 0:

                #find the earliest of the unanswered questions
                # redirect to it.
                first_question=unanswered_questions.order_by('id')[:1].get()

                return HttpResponseRedirect(
                    reverse('quiz:question',
                            kwargs={'question_id':first_question.id,
                                    'pk':quiz.id, 'attempt':attempt_id}))

            else:
                answers = Answer.objects.filter(question__in=quiz_questions)
                results = AnswersSubmitted.objects.filter(question__in=quiz_questions,
                                                          attempt=ATTEMPT)
                selected_answers = Answer.objects.filter(answerssubmitted__in=results)
                # determine the score the percentage of answers correct
                correct_answers=selected_answers.filter(correct_bool=True).count()
                all_answers=selected_answers.count()
                score=correct_answers / all_answers *100
                QuizAttempt.objects.filter(id=attempt_id).update(score=score)

                return HttpResponseRedirect(
                    reverse('quiz:submitQuiz', kwargs={'pk':quiz.id,
                                                    'attempt':attempt_id}))
        return HttpResponseRedirect('/quiz/')

    def days_hours_minutes_seconds(self, time):
        days = time.days
        hours = time.seconds//3600
        minutes = (time.seconds//60)%60
        seconds = time.seconds%60
        return {'days':days, 'hours':hours, 'minutes':minutes,
                'seconds':seconds}


class SubmitQuizView(LoginRequiredMixin, generic.TemplateView):
    login_url = '/account/login/'
    redirect_field_name = 'redirect_to'
    template_name='quiz/submitQuiz.html'

    def calculateProgress(self, user, quiz_questions, attempt):
        answered_questions=AnswersSubmitted.objects.filter(user=user).filter(attempt=attempt).aggregate(Count('question'))
        total_questions=quiz_questions.aggregate(Count('id'))
        num_total_questions=total_questions.get('id__count')
        num_answered_questions=answered_questions.get('question__count')
        progress = num_answered_questions / num_total_questions * 100
        return progress

    def get(self, request, *args, **kwargs):
        #The goal is to display the results of that attempt of the quiz
        quiz_id = self.kwargs.pop('pk')
        attempt_id = self.kwargs.pop('attempt')
        quiz = Quiz.objects.get(id=quiz_id)
        attempt = QuizAttempt.objects.get(id=attempt_id)
        questions = Question.objects.filter(quiz=quiz)

        answers = Answer.objects.filter(question__in=questions)
        results = AnswersSubmitted.objects.filter(question__in=questions,
                                                  attempt=attempt)
        selected_answers = Answer.objects.filter(answerssubmitted__in=results)

        answered_questions = results.values('question')
        unanswered_questions = questions.exclude(
            id__in=answered_questions)
        answered_questions=questions.filter(id__in=answered_questions)

        answered_questions = answered_questions.annotate(
            answered_bool=Value(True, BooleanField()))
        unanswered_questions = unanswered_questions.annotate(
            answered_bool=Value(False, BooleanField()))
        status_questions = answered_questions.union(unanswered_questions).order_by('id')

        # report the score and the time_taken
        progress=self.calculateProgress(request.user, questions, attempt)
        return render(request, self.template_name,
                      {'quiz':quiz,
                       'results':results, 'attempt_id':attempt_id,
                       'questions':status_questions, 'answers':answers,
                       'selected_answers':selected_answers,
                       'progress':progress
                       })

    def post(self, request, *args, **kwargs):
        quiz_id = self.kwargs.pop('pk')
        attempt_id = self.kwargs.pop('attempt')

        # determine the time taken
        last_time=QuizAttempt.objects.get(id=attempt_id).finish_time
        start_time=QuizAttempt.objects.get(id=attempt_id).start_time
        time_taken=last_time-start_time
        QuizAttempt.objects.filter(id=attempt_id).update(finish_time=datetime.now())
        last_time=QuizAttempt.objects.get(id=attempt_id).finish_time
        start_time=QuizAttempt.objects.get(id=attempt_id).start_time
        time_taken=last_time-start_time

        QuizAttempt.objects.filter(id=attempt_id).update(time_taken=time_taken)
        # update submitted_bool to True
        QuizAttempt.objects.filter(id=attempt_id).update(submitted_bool=True)


        print("potatoes are not green, unless bad ")
        return HttpResponseRedirect(
            reverse('quiz:endQuiz', kwargs={'pk':quiz_id,
                                               'attempt':attempt_id}))


class EndOfQuizView(LoginRequiredMixin, generic.TemplateView):
    login_url = '/account/login/'
    redirect_field_name = 'redirect_to'
    template_name='quiz/endQuiz.html'

    def get(self, request, *args, **kwargs):
        #The goal is to display the results of that attempt of the quiz
        quiz_id = self.kwargs.pop('pk')
        attempt_id = self.kwargs.pop('attempt')
        quiz = Quiz.objects.get(id=quiz_id)
        attempt = QuizAttempt.objects.get(id=attempt_id)
        questions = Question.objects.filter(quiz=quiz)

        answers = Answer.objects.filter(question__in=questions)
        results = AnswersSubmitted.objects.filter(question__in=questions,
                                                  attempt=attempt)
        selected_answers=Answer.objects.filter(answerssubmitted__in=results)
        # report the score and the time_taken
        score= attempt.score
        time_taken=self.days_hours_minutes_seconds(attempt.time_taken)

        return render(request, self.template_name,
                      {'quiz':quiz, 'time_taken':time_taken,
                       'results':results,
                       'questions':questions, 'answers':answers,
                       'selected_answers':selected_answers,
                       'score':score})
    
    def days_hours_minutes_seconds(self, time):
        days = time.days
        hours = time.seconds//3600
        minutes = (time.seconds//60)%60
        seconds = time.seconds%60
        return {'days':days, 'hours':hours, 'minutes':minutes,
                'seconds':seconds}
    
