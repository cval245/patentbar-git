from django.urls import path

from . import views

app_name = 'quiz'
urlpatterns = [
    # ex: /quiz/
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.QuizDetailView.as_view(), name='detail'),
    path('<int:pk>/question<int:question_id>', views.QuestionView.as_view(),
         name='question')
]
