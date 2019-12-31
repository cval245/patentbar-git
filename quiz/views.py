from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import generic

from .forms import  AnswerForm, QuizStartForm
from .models import Answer, Question, Quiz
from userProfile.models import AnswersSubmitted, QuizAttempt
from datetime import datetime
# Create your views here.

def HomePageView(request):
    return HttpResponse('<html><title>Patent-Bar</title></html>')

class IndexView(generic.ListView):
    template_name = 'quiz/index.html'
    context_object_name = 'quiz'

    def get_queryset(self):
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
            print("Running man", quiz)
            submission = QuizAttempt.objects.create(user=1,
                                                    quiz=quiz,
                                                    finish_time=finish_time)
            return HttpResponseRedirect('/quiz/')
        return HttpResponseRedirect('/quiz/')

class QuestionView(generic.CreateView):
    form_class = AnswerForm
    template_name = 'quiz/question.html'
    model = Question

    def get(self, request, *args, **kwargs):
        question_id = self.kwargs.pop('question_id')
        form = self.form_class(request.GET or None, question=question_id)
        return render(request, self.template_name, {'form':form})

    def post(self, request, *args, **kwargs):
        question_id = self.kwargs.pop('question_id')
        QUESTION = Question.objects.get(id=question_id)
        form = self.form_class(request.POST, question=question_id)
        if form.is_valid():
            ANSWER = form.cleaned_data['choice']
            submission = AnswersSubmitted.objects.create(user=1,
                                                         question=QUESTION,
                                                         answer=ANSWER)
            return HttpResponseRedirect('/quiz/')
        return HttpResponseRedirect('/quiz/')

