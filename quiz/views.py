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

class IndexView(generic.ListView):
    template_name = 'quiz/index.html'
    context_object_name = 'quiz'

    def get_queryset(self):
        print("singing")
        print(Quiz.objects.order_by('title'))
        """Return all the quizzes"""
        return Quiz.objects.order_by('title')

class QuizDetailView(generic.DetailView):
    template_name = 'quiz/detail.html'
    model = Quiz
    form_class = QuizStartForm

    def get(self, request, *args, **kwargs):
        form = self.form_class(request.GET or None)
        return render(request, self.template_name, {'form':form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        finish_time=datetime(2000, 1, 1, 0, 0, 0, 0) # default placeholder
        if form.is_valid():
            quiz = form.cleaned_data['quizzes']
            submission = QuizAttempt.objects.create(user=request.user,
                                                    quiz=quiz,
                                                    finish_time=finish_time)
            first_question=Question.objects.filter(quiz=quiz).first()
            return HttpResponseRedirect(
                reverse('quiz:question',
                        kwargs={'question_id':first_question.id,
                                'pk':quiz.id,
                                'attempt':submission.id}))
        return HttpResponseRedirect('/quiz/')


class QuestionView(generic.CreateView):
    form_class = AnswerForm
    template_name = 'quiz/question.html'
    model = Question

    def get(self, request, *args, **kwargs):
        question_id = self.kwargs.pop('question_id')
        form = self.form_class(request.GET or None, question=question_id)
        question = Question.objects.get(id=question_id)
        return render(request, self.template_name,
                      {'form':form, 'question':question})

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

            if quiz_questions.filter(id=next_question_id):
                next_question=quiz_questions.get(id=next_question_id)
                return HttpResponseRedirect(
                    reverse('quiz:question',
                            kwargs={'question_id':next_question_id,
                                    'pk':quiz.id, 'attempt':attempt_id}))
            else:
                print(QuizAttempt.objects.filter(id=attempt_id).values('start_time'))
                #difference_time = self.days_hours_minutes_seconds(QuizAttempt.objects.filter(id=attempt_id).values('finish_time')-QuizAttempt.objects.filter(id=attempt_id).values('start_time'))
                QuizAttempt.objects.filter(id=attempt_id).update(finish_time=datetime.now())
                return HttpResponseRedirect(
                    reverse('quiz:endQuiz', kwargs={'pk':quiz.id,
                                                    'attempt':attempt_id}))
        return HttpResponseRedirect('/quiz/')

    def days_hours_minutes_seconds(self, time):
        days = time.days
        hours = time.seconds//3600
        minutes = (time.seconds//60)%60
        seconds = time.seconds%60
        return {'days':days, 'hours':hours, 'minutes':minutes,
                'seconds':seconds}


class EndOfQuizView(generic.TemplateView):
    template_name='quiz/endQuiz.html'
    def get(self, request, *args, **kwargs):
        #The goal is to display the results of that attempt of the quiz
        quiz_id = self.kwargs.pop('pk')
        attempt_id = self.kwargs.pop('attempt')
        quiz = Quiz.objects.get(id=quiz_id)
        attempt = QuizAttempt.objects.get(id=attempt_id)
        questions = Question.objects.filter(quiz=quiz)
        time = attempt.finish_time - attempt.start_time

        time_taken=self.days_hours_minutes_seconds(time)
        answers = Answer.objects.filter(question__in=questions)
        results = AnswersSubmitted.objects.filter(question__in=questions,
                                                  attempt=attempt)
        selected_answers = Answer.objects.filter(answerssubmitted__in=results)

        return render(request, self.template_name,
                      {'quiz':quiz, 'time_taken':time_taken, 'results':results,
                       'questions':questions, 'answers':answers,
                       'selected_answers':selected_answers})
    
    def days_hours_minutes_seconds(self, time):
        days = time.days
        hours = time.seconds//3600
        minutes = (time.seconds//60)%60
        seconds = time.seconds%60
        return {'days':days, 'hours':hours, 'minutes':minutes,
                'seconds':seconds}
    
