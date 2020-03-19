from django.test import Client, TestCase
from django.test import Client, TestCase
from django.utils import timezone
from django.contrib import auth
import datetime

from userProfile.models import AnswersSubmitted, QuizAttempt
from quiz.models import Answer, Question, Quiz
from users.models import CustomUser
# Create your tests here.

class AnswersSubmittedModelTest(TestCase):

    def setUp(self):
        self.client = Client()
        user=CustomUser.objects.create_user('test_UserProfile',
                                             email='a@a.net',
                                             password='abc123')
        user.save()

    def test_UserProfileAnswersSubmitted_Foreign_Keys(self):
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
        self.client.login(username='test_UserProfile', password='abc123')
        AnswersSubmitted.objects.create(id=submitted_id,
                                        user=auth.get_user(self.client),
                                        question=QUESTION,
                                        answer=ANSWER,)

    # Need to add attempt No. for each userProfileAnswersSubmitted
    def test_QuizAttempt_contains_dates(self):
        quiz_id = 1
        user_id = 1
        finish_time = timezone.now() + datetime.timedelta(0,5)
        self.client.login(username='test_UserProfile', password='abc123')
        QUIZ = Quiz.objects.create(id=quiz_id,
                             title="AnswersSubmitted Quiz 1")
        QuizAttempt.objects.create(user = auth.get_user(self.client),
                                   quiz = QUIZ,
                                   finish_time = finish_time)

    def test_QuizAttempt_contains_current_user(self):
        self.client.login(username='test_UserProfile', password='abc123')
        quiz_id = 1
        finish_time = timezone.now() + datetime.timedelta(0,5)
        QUIZ = Quiz.objects.create(id=quiz_id,
                             title="AnswersSubmitted Quiz 1")
        QuizAttempt.objects.create(user = auth.get_user(self.client),
                                   quiz = QUIZ,
                                   finish_time = finish_time)

    # Need to add attempt No. for each quiz

