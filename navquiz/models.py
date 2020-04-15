from django.db import models

# Create your models here.

class NavQuestion(models.Model):
    text = models.TextField()
    def __str__(self):
        return self.text

class NavAnswer(models.Model):
    question = models.ForeignKey(NavQuestion, on_delete=models.CASCADE)
    mpep_chapter = models.IntegerField()
    mpep_article = models.DecimalField(max_digits=5, decimal_places=3)
    mpep_location = models.CharField(max_length=50)
    section_title = models.TextField()

    def __str__(self):
        return self.text
