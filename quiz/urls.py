from django.urls import path

from . import views

app_name = 'quiz'
urlpatterns = [
    # ex: /quiz/
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.QuizDetailView.as_view(), name='detail'),
    path('<int:pk>/attempt<int:attempt>/question<int:question_id>',
         views.QuestionView.as_view(), name='question'),
    path('<int:pk>/attempt<int:attempt>/endquiz',
         views.EndOfQuizView.as_view(), name='endQuiz'),
    path('<int:pk>/attempt<int:attempt>/submitquiz',
         views.SubmitQuizView.as_view(), name='submitQuiz'),
]
