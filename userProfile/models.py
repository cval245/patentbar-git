from django.db import models
from quiz.models import Answer, Question, Quiz
# Create your models here.

class AnswersSubmitted(models.Model):
    user = models.IntegerField()
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

class QuizAttempt(models.Model):
    user = models.IntegerField()
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    finish_time = models.DateTimeField()
