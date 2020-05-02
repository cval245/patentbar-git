from django.urls import path

from . import views

app_name = 'navquiz'
urlpatterns = [
    # ex: /navquiz/
    path('', views.StartNavQuiz.as_view(), name='startNavQuiz'),
    path('attempt<int:user_attempt>/question<int:question_id>',
         views.QuestionView.as_view(), name='question'),
    path('attempt<int:user_attempt>/endquiz',
         views.EndOfQuizView.as_view(), name='endQuiz'),
]
