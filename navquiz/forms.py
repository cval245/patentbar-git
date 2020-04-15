from django import forms
from userProfile.models import NavAnswersSubmitted

class QuestionForm(forms.ModelForm):
    class Meta:
        model = NavAnswersSubmitted
        fields = ['article_submitted']
        #widgets = {'article_submitted': forms.TextInput()}



