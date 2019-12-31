from django import forms
from .models import Answer, Quiz

class AnswerForm(forms.Form):
    QUERYSET = Answer.objects.all()
    choice = forms.ModelChoiceField(queryset=QUERYSET,
                                    empty_label=None,
                                    widget=forms.RadioSelect,
                                    error_messages=
                                    {'required':'Please select an answer'},)

    def __init__(self, *args, **kwargs):
        QUESTION = kwargs.pop('question', None)
        super(AnswerForm, self).__init__(*args, **kwargs)
        self.fields['choice'].queryset = Answer.objects.filter(question=QUESTION)

class QuizStartForm(forms.Form):
    quizzes = forms.ModelChoiceField(queryset=Quiz.objects.all())


#class QuizStartForm(forms.Form):
#    QUERYSET = Quiz.objects.all()
#    quizzes = forms.ModelChoiceField(queryset=QUERYSET,
#                                     empty_label="Select Test")

    # def __init__(self, *args, **kwargs):
    #     quiz = kwargs.pop('quiz', None)
    #     super(QuizStartForm, self).__init__(*args, **kwargs)
    #     self.fields['quizzes'].queryset = Quiz.objects.filter(id=quiz)
