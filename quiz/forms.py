from django import forms
from .models import Answer

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
