from django.shortcuts import render
from django.views import generic

from .models import Quiz

# Create your views here.

class IndexView(generic.ListView):
    template_name = 'quiz/index.html'

    def get_queryset(self):
        """Return all the quizzes"""
        return Quiz.objects.order_by('quiz_title')
