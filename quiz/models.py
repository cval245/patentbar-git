from django.db import models

# Create your models here.

class Quiz(models.Model):
    title = models.TextField()
    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.TextField()
    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()
    correct_bool = models.BooleanField()
    explanation = models.TextField()

    def __str__(self):
        return self.text
