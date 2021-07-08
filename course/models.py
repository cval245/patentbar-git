from django.db import models
from django.core.exceptions import ValidationError
#from quiz.models import Answer, Question, Quiz
from quiz.models import Quiz

# Create your models here.

class Course(models.Model):
     title = models.TextField()
     order_no=models.IntegerField()
     def __str__(self):
          return self.title

class Module(models.Model):
     title = models.TextField()
     course = models.ForeignKey(Course, on_delete=models.CASCADE)
     order_no = models.IntegerField()
     quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE,
                              blank=True,
                              null=True)
     def __str__(self):
          return self.title

     def validate_unique(self, *args, **kwargs):
          super(Module, self).validate_unique(*args, **kwargs)

          if self.__class__.objects.filter(course=self.course, order_no=self.order_no).exists():
               raise ValidationError(
                    message="""Module with this (course, order_no) already exists,
                    try to use a new order_no"""
               )

class Content(models.Model):
     title = models.TextField()
     text = models.TextField()
     module = models.ForeignKey(Module, on_delete=models.CASCADE)
     def __str__(self):
          return self.title

