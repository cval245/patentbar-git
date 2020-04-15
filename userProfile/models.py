from django.db import models
from quiz.models import Answer, Question, Quiz
from navquiz.models import NavQuestion, NavAnswer

import datetime
# Create your models here.

class QuizAttempt(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    finish_time = models.DateTimeField()
    score = models.DecimalField(max_digits=5, decimal_places=2)
    time_taken = models.DurationField(default=datetime.timedelta())
    submitted_bool = models.BooleanField(default=False)

class AnswersSubmitted(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE)


class NavQuizAttempt(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    finish_time = models.DateTimeField()
    score = models.DecimalField(max_digits=5, decimal_places=2)
    time_taken = models.DurationField(default=datetime.timedelta())
    submitted_bool = models.BooleanField(default=False)

class NavAnswersSubmitted(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    article_submitted = models.DecimalField(max_digits=5, decimal_places=3,
                                            default = 0)
    question = models.ForeignKey(NavQuestion, on_delete=models.CASCADE)
    attempt = models.ForeignKey(NavQuizAttempt, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    finish_time = models.DateTimeField()
    time_taken = models.DurationField(default=datetime.timedelta())
