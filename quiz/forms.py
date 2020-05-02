from django import forms
from .models import Answer, Quiz

class AnswerForm(forms.Form):
    choice = forms.ModelChoiceField(queryset=None,
                                    empty_label=None,
                                    widget=forms.RadioSelect,
                                    error_messages=
                                    {'required':'Please select an answer'},)

    def __init__(self, *args, **kwargs):
        QUESTION = kwargs.pop('question', None)
        super(AnswerForm, self).__init__(*args, **kwargs)
        self.fields['choice'].queryset = Answer.objects.filter(question=QUESTION).order_by('id')

