from django.http import HttpResponse
from django.shortcuts import render
from django.views import generic

from .models import Quiz

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
    context_object_name = 'quiz_title'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz_id = self.kwargs.pop('pk')
        context['quiz_title'] = Quiz.objects.get(id=quiz_id).title
        return context
