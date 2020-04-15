from django.urls import path, re_path, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'
urlpatterns = [
    # ex path is /account/
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('', include('django.contrib.auth.urls')),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('results/', views.ResultsView.as_view(), name='results'),
    path('results/quiz=<int:pk>/', views.QuizResultsView.as_view(),
         name='quizResults'),
]
