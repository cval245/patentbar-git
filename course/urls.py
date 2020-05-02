from django.urls import path

from . import views
app_name='course'
urlpatterns = [
    path('', views.MainCourseView.as_view(), name='main_course'),
    path('<int:course_id>/', views.CourseView.as_view(), name='course'),
    path('<int:course_id>/module<int:module_id>/',
         views.ModuleView.as_view(), name='module'),
]
