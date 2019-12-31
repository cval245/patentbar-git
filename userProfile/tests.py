from django.test import Client, TestCase
from userProfile.models import AnswersSubmitted, QuizAttempt
from quiz.models import Answer, Question, Quiz
from django.utils import timezone

import datetime
# Create your tests here.

class AnswersSubmittedModelTest(TestCase):

    def setup(self):
        self.client = Client()

    def test_UserProfileAnswersSubmitted_Foreign_Keys(self):
        #userProfileAnswersSubmitted.objects.get(id=1)
        answer_id = 1
        submitted_id =1
        user_id = 1
        question_id = 1
        quiz_id = 1
        QUIZ = Quiz.objects.create(id=quiz_id,
                             title="AnswersSubmitted Quiz 1")

        QUESTION = Question.objects.create(id=question_id, quiz=QUIZ,
                                text="AnswersSubmitted Question1")


        ANSWER = Answer.objects.create(id=answer_id, question=QUESTION,
                              text="AnswersSubmitted Answer 1")

        AnswersSubmitted.objects.create(id=submitted_id,
                                        user=user_id,
                                        question=QUESTION,
                                        answer=ANSWER,)

    # Need to add attempt No. for each userProfileAnswersSubmitted
    def test_QuizAttempt_contains_dates(self):
        quiz_id = 1
        user_id = 1
        finish_time = timezone.now() + datetime.timedelta(0,5)
        QUIZ = Quiz.objects.create(id=quiz_id,
                             title="AnswersSubmitted Quiz 1")
        QuizAttempt.objects.create(user = user_id,
                                   quiz = QUIZ,
                                   finish_time = finish_time)
    # Need to add attempt No. for each quiz

