from django.db import models
#from quiz.models import Answer, Question, Quiz
from quiz.models import Quiz

# Create your models here.


# class ContentCollection(models.Model):
#      content=models.TextField()
#      #This is meant to have an app corresponding to the Quiz app. 
# class Course(models.Model): 
#     title=models.TextField()
#     quiz_collection=models.ForeignKey(QuizCollection,
#                                       on_delete=models.CASCADE)
#     content_collection=models.ForeignKey(ContentCollection,
#                                          on_delete=models.CASCADE)

class QuizCollection(models.Model):
     quiz=models.ForeignKey(Quiz, on_delete=models.CASCADE)

