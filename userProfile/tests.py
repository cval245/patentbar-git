from django.test import Client, TestCase
from django.utils import timezone
from django.contrib import auth
import datetime
from django.utils import timezone
from django.db.models import Count

from userProfile.models import AnswersSubmitted, QuizAttempt
from userProfile.models import NavQuizAttempt, NavAnswersSubmitted
from quiz.models import Answer, Question, Quiz
from navquiz.models import NavQuestion, NavAnswer
from users.models import CustomUser
# Create your tests here.


class QuizAttemptModelTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.client.login(username='test_UserProfile', password='abc123')
    @classmethod
    def setUpTestData(cls):
        cls.user=CustomUser.objects.create_user('test_UserProfile',
                                            email='a@a.net',
                                            password='abc123')
        cls.user.save()
        cls.quiz_one=Quiz.objects.create(id=1, title = "Testing Quiz 1")
        cls.quiz_two=Quiz.objects.create(id=2, title = "Testing Quiz 2")
        cls.question_one=Question.objects.create(quiz=cls.quiz_one,
                                             text='question_one')
        cls.question_two=Question.objects.create(quiz=cls.quiz_one,
                                             text='question_two')
        cls.answer_one=Answer.objects.create(question=cls.question_one,
                                         text='answer_one',
                                         correct_bool=True,
                                         explanation='default')
        cls.answer_two=Answer.objects.create(question=cls.question_one,
                                         text='answer_two',
                                         correct_bool=False,
                                         explanation='default')
        cls.answer_three=Answer.objects.create(question=cls.question_two,
                                           text='answer_three',
                                           correct_bool=True,
                                           explanation='default')
        cls.answer_four=Answer.objects.create(question=cls.question_two,
                                           text='answer_four',
                                           correct_bool=False,
                                           explanation='default')
        cls.attempt_one=QuizAttempt.objects.create(user=cls.user,
                                   quiz=cls.quiz_one,
                                   finish_time=timezone.now(),
                                   score=0,
                                    user_attempt_no=1)
        cls.attempt_two=QuizAttempt.objects.create(user=cls.user,
                                   quiz=cls.quiz_one,
                                   finish_time=timezone.now(),
                                   score=0,
                                   user_attempt_no=2)


    # Test if set_user_attempt_no function returns 1 for attempt_no with
    # a quiz that hasn't been attempted before
    def test_QuizAttemptGet_next_user_attempt_no_empty_prior(self):
        user = auth.get_user(self.client)
        quiz_one = Quiz.objects.get(id=1)
        quiz_two = Quiz.objects.get(id=2)
        attempt = QuizAttempt.objects.create(user=user,
                                             quiz=quiz_two,
                                             finish_time=timezone.now(),
                                             score=0,
                                             user_attempt_no=0)

        next_quiz = quiz_two

        next_attempt_no = attempt.get_next_user_attempt_no()
        assert next_attempt_no == 1

    # Test if set_user_attempt_no function returns 3 for attempt_no with
    # a quiz that HAS been attempted before (it really just needs to returns
    # the previous attempt_no plus one)
    def test_QuizAttemptGet_next_user_attempt_no_true_existing(self):
        user = auth.get_user(self.client)
        quiz_one= Quiz.objects.get(id=2)
        next_quiz = quiz_one

        attempt = QuizAttempt.objects.create(user=user,
                                             quiz=quiz_one,
                                             finish_time=timezone.now(),
                                             score=0,
                                             user_attempt_no=0)

        attempt_1 = QuizAttempt.objects.create(user=user,
                                             quiz=quiz_one,
                                             finish_time=timezone.now(),
                                             score=0,
                                             user_attempt_no=1)
        next_attempt_no = attempt.get_next_user_attempt_no()

        assert next_attempt_no == 2

    def test_QuizAttemptCalculateProgress(self):
        user=auth.get_user(self.client)
        quiz_one=Quiz.objects.get(id=1)
        question_one=Question.objects.get(id=1)
        answer_one=Answer.objects.get(id=1)
        attempt=QuizAttempt.objects.get(user=user,quiz=quiz_one,
                                        user_attempt_no=1)
        AnswersSubmitted.objects.create(user=user,answer=answer_one,
                                        question=question_one,
                                        attempt=attempt)

        progress=attempt.progress()
        assert progress == 50


    def test_CalculateScoreIsCorrect(self):
        user=auth.get_user(self.client)
        quiz_one=Quiz.objects.get(id=1)
        question_one=Question.objects.get(id=1)
        question_two=Question.objects.get(id=2)
        answer_one=Answer.objects.get(id=1)
        answer_three=Answer.objects.get(id=3)
        attempt=QuizAttempt.objects.get(user=user,quiz=quiz_one,
                                        user_attempt_no=1)
        AnswersSubmitted.objects.create(user=user,answer=answer_one,
                                        question=question_one,
                                        attempt=attempt)
        AnswersSubmitted.objects.create(user=user,answer=answer_three,
                                        question=question_two,
                                        attempt=attempt)

        score = attempt.calculate_score()
        assert score == 100

    def test_SetScore(self):
        user=auth.get_user(self.client)
        quiz_one=Quiz.objects.get(id=1)
        question_one=Question.objects.get(id=1)
        question_two=Question.objects.get(id=2)
        answer_one=Answer.objects.get(id=1)
        answer_three=Answer.objects.get(id=3)
        attempt=QuizAttempt.objects.get(user=user,quiz=quiz_one,
                                        user_attempt_no=1)
        AnswersSubmitted.objects.create(user=user,answer=answer_one,
                                        question=question_one,
                                        attempt=attempt)
        AnswersSubmitted.objects.create(user=user,answer=answer_three,
                                        question=question_two,
                                        attempt=attempt)
        print(attempt.calculate_score())
        attempt.set_score()
        assert attempt.score == 100

    def test_TrueIfAnswered_NotAnswered(self):
        user=auth.get_user(self.client)
        quiz_one=Quiz.objects.get(id=1)
        question_one=Question.objects.get(id=1)
        question_two=Question.objects.get(id=2)
        answer_one=Answer.objects.get(id=1)
        attempt=QuizAttempt.objects.get(user=user,quiz=quiz_one,
                                        user_attempt_no=1)

        submitted=AnswersSubmitted.objects.create(user=user,
                                                  answer=answer_one,
                                                  question=question_one,
                                                  attempt=attempt)
        answered_bool = attempt.true_if_answered(question_two)

        assert False == answered_bool

    def test_TrueIfAnswered_Answered(self):
        user=auth.get_user(self.client)
        quiz_one=Quiz.objects.get(id=1)
        question_one=Question.objects.get(id=1)
        question_two=Question.objects.get(id=2)
        answer_one=Answer.objects.get(id=1)
        attempt=QuizAttempt.objects.get(user=user,quiz=quiz_one,
                                        user_attempt_no=1)

        submitted=AnswersSubmitted.objects.create(user=user,
                                                  answer=answer_one,
                                                  question=question_one,
                                                  attempt=attempt)
        answered_bool = attempt.true_if_answered(question_one)

        assert True == answered_bool

class AnswersSubmittedModelTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.client.login(username='test_UserProfile', password='abc123')
        
    @classmethod
    def setUpTestData(cls):
        cls.user=CustomUser.objects.create_user('test_UserProfile',
                                            email='a@a.net',
                                            password='abc123')
        cls.user.save()
        cls.quiz_one=Quiz.objects.create(id=1, title = "Testing Quiz 1")
        cls.quiz_two=Quiz.objects.create(id=2, title = "Testing Quiz 2")
        cls.question_one=Question.objects.create(id=1,quiz=cls.quiz_one,
                                             text='question_one')
        cls.question_two=Question.objects.create(id=2,quiz=cls.quiz_one,
                                             text='question_two')
        cls.answer_one=Answer.objects.create(id=1,question=cls.question_one,
                                         text='answer_one',
                                         correct_bool=True,
                                         explanation='default')
        cls.answer_two=Answer.objects.create(id=2,question=cls.question_one,
                                         text='answer_two',
                                         correct_bool=False,
                                         explanation='default')
        cls.answer_three=Answer.objects.create(id=3,question=cls.question_two,
                                           text='answer_three',
                                           correct_bool=True,
                                           explanation='default')
        cls.answer_four=Answer.objects.create(id=4,question=cls.question_two,
                                           text='answer_four',
                                           correct_bool=False,
                                           explanation='default')
        cls.attempt_one=QuizAttempt.objects.create(user=cls.user,
                                   quiz=cls.quiz_one,
                                   finish_time=timezone.now(),
                                   score=0,
                                   user_attempt_no=1)
        cls.attempt_two=QuizAttempt.objects.create(user=cls.user,
                                   quiz=cls.quiz_one,
                                   finish_time=timezone.now(),
                                   score=0,
                                   user_attempt_no=2)
        cls.attempt_True=QuizAttempt.objects.create(user=cls.user,
                                   quiz=cls.quiz_one,
                                   finish_time=timezone.now(),
                                   score=0,
                                submitted_bool=True,
                                   user_attempt_no=3)


    def test_AnswersSubmtetedtIsLastQuestionFalse(self):
        user=auth.get_user(self.client)
        quiz_one=Quiz.objects.get(id=1)
        question_one=Question.objects.get(id=1)
        answer_one=Answer.objects.get(id=1)
        attempt=QuizAttempt.objects.get(user=user,quiz=quiz_one,
                                        user_attempt_no=1)
        submitted=AnswersSubmitted.objects.create(user=user,answer=answer_one,
                                        question=question_one,
                                        attempt=attempt)

        assert submitted.isLastUnAnsweredQuestion() == False

    def test_AnswersSubmtetedtIsLastQuestionTrue(self):
        user=auth.get_user(self.client)
        quiz_one=Quiz.objects.get(id=1)
        question_one=Question.objects.get(id=1)
        question_two=Question.objects.get(id=2)
        answer_one=Answer.objects.get(id=1)
        answer_two=Answer.objects.get(id=2)
        attempt=QuizAttempt.objects.get(user=user,quiz=quiz_one,
                                        user_attempt_no=1)
        submitted_one=AnswersSubmitted.objects.create(user=user,answer=answer_one,
                                        question=question_one,
                                        attempt=attempt)
        submitted_two=AnswersSubmitted.objects.create(user=user,answer=answer_two,
                                        question=question_one,
                                        attempt=attempt)

        assert submitted_two.isLastUnAnsweredQuestion() == True

    def test_AnswersSubmittedtGetFirstUnansweredQuestion(self):
        user=auth.get_user(self.client)
        quiz_one=Quiz.objects.get(id=1)
        question_one=Question.objects.get(id=1)
        question_two=Question.objects.get(id=2)
        answer_one=Answer.objects.get(id=1)
        answer_two=Answer.objects.get(id=2)
        attempt=QuizAttempt.objects.get(user=user,quiz=quiz_one,
                                        user_attempt_no=1)
        submitted_two=AnswersSubmitted.objects.create(user=user,
                                                      answer=answer_two,
                                                      question=question_two,
                                                      attempt=attempt)
        question = submitted_two.getFirstUnansweredQuestion()
        assert question == question_one

    def test_AnswersSubmittedtGetNextQuestionNextID(self):
        user=auth.get_user(self.client)
        quiz_one=Quiz.objects.get(id=1)
        question_one=Question.objects.get(id=1)
        question_two=Question.objects.get(id=2)
        answer_one=Answer.objects.get(id=1)
        answer_two=Answer.objects.get(id=2)
        attempt=QuizAttempt.objects.get(user=user,quiz=quiz_one,
                                        user_attempt_no=1)
        submitted_one=AnswersSubmitted.objects.create(user=user,
                                                      answer=answer_one,
                                                      question=question_one,
                                                      attempt=attempt)
        question = submitted_one.getNextQuestion()
        assert question == question_two

    def test_AnswersSubmittedtGetNextQuestionFindsUnanswered(self):
        user=auth.get_user(self.client)
        quiz_one=Quiz.objects.get(id=1)
        question_one=Question.objects.get(id=1)
        question_two=Question.objects.get(id=2)
        answer_one=Answer.objects.get(id=1)
        answer_two=Answer.objects.get(id=2)
        attempt=QuizAttempt.objects.get(user=user,quiz=quiz_one,
                                        user_attempt_no=1)


        submitted_two=AnswersSubmitted.objects.create(user=user,
                                                      answer=answer_two,
                                                      question=question_two,
                                                      attempt=attempt)
        question = submitted_two.getNextQuestion()
        assert question == question_one

    def test_AnswersSubmittedtGetNextQuestionAllQuestionsAnswered(self):
        user=auth.get_user(self.client)
        quiz_one=Quiz.objects.get(id=1)
        question_one=Question.objects.get(id=1)
        question_two=Question.objects.get(id=2)
        answer_one=Answer.objects.get(id=1)
        answer_two=Answer.objects.get(id=2)
        attempt=QuizAttempt.objects.get(user=user,quiz=quiz_one,
                                        user_attempt_no=1)
        submitted_one=AnswersSubmitted.objects.create(user=user,
                                                      answer=answer_one,
                                                      question=question_one,
                                                      attempt=attempt)
        submitted_two=AnswersSubmitted.objects.create(user=user,
                                                      answer=answer_two,
                                                      question=question_two,
                                                      attempt=attempt)
        question = submitted_two.getNextQuestion()
        assert question == None

    def test_setAnswerSubmittedFalse(self):
        user=auth.get_user(self.client)
        quiz_one=Quiz.objects.get(id=1)
        question_one=Question.objects.get(id=1)
        answer_one=Answer.objects.get(id=1)
        answer_two=Answer.objects.get(id=2)
        attempt=QuizAttempt.objects.get(user=user,quiz=quiz_one,
                                        user_attempt_no=1)
        submitted_one=AnswersSubmitted.objects.create(user=user,
                                                      answer=answer_one,
                                                      question=question_one,
                                                      attempt=attempt)
        submitted_one.setAnswer(answer_two)

        assert submitted_one.answer == answer_two

    def test_setAnswerSubmittedTrue(self):
        user=auth.get_user(self.client)
        quiz_one=Quiz.objects.get(id=1)
        question_one=Question.objects.get(id=1)
        answer_one=Answer.objects.get(id=1)
        answer_two=Answer.objects.get(id=2)
        attempt_true=QuizAttempt.objects.get(user=user,quiz=quiz_one,
                                        user_attempt_no=3)
        submitted_one=AnswersSubmitted.objects.create(user=user,
                                                      answer=answer_one,
                                                      question=question_one,
                                                      attempt=attempt_true)
        submitted_one.setAnswer(answer_two)

        assert submitted_one.answer == answer_one

class NavQuizAttemptModelTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.client.login(username='test_UserProfile', password='abc123')
        
    @classmethod
    def setUpTestData(cls):
        cls.user=CustomUser.objects.create_user('test_UserProfile',
                                            email='a@a.net',
                                            password='abc123')
        cls.user.save()

        navQuestion1 = NavQuestion.objects.create(text='NavQuestion1 name')
        navQuestion2 = NavQuestion.objects.create(text='NavQuestion2 name')
        navQuestion3 = NavQuestion.objects.create(text='NavQuestion3 name')
        navQuestion4 = NavQuestion.objects.create(text='NavQuestion4 name')
        navQuestion5 = NavQuestion.objects.create(text='NavQuestion5 name')
        navQuestion6 = NavQuestion.objects.create(text='NavQuestion6 name')
        navAnswer1 = NavAnswer.objects.create(question=navQuestion1,
                                              mpep_chapter=1,
                                              mpep_article=1,
                                              mpep_location='1',
                                              section_title='navAnswer1')
        navAnswer2 = NavAnswer.objects.create(question=navQuestion2,
                                              mpep_chapter=2,
                                              mpep_article=2,
                                              mpep_location='2',
                                              section_title='navAnswer2')
        navAnswer3 = NavAnswer.objects.create(question=navQuestion3,
                                              mpep_chapter=3,
                                              mpep_article=3,
                                              mpep_location='3',
                                              section_title='navAnswer3')

        navAttempt=NavQuizAttempt.objects.create(user=cls.user,
                                                 finish_time=timezone.now(),
                                                 score=0,
                                                 user_attempt_no=1)

    def test_NavQuizAttemptCalculateProgress(self):
        user=auth.get_user(self.client)

        navQuestion_one=NavQuestion.objects.get(id=1)
        navQuestion_two=NavQuestion.objects.get(id=2)
        navAttempt=NavQuizAttempt.objects.get(id=1 )
        NavAnswersSubmitted.objects.create(user=user,
                                           article_submitted='1',
                                           question=navQuestion_one,
                                           attempt=navAttempt,
                                           start_time=timezone.now(),
                                           finish_time=timezone.now(),
                                           submitted_bool=True,
                                           correct_bool=True)
        NavAnswersSubmitted.objects.create(user=user,
                                           article_submitted='2',
                                           question=navQuestion_two,
                                           attempt=navAttempt,
                                           start_time=timezone.now(),
                                           finish_time=timezone.now(),
                                           submitted_bool=False,
                                           correct_bool=False)

        progress=navAttempt.progress()
        assert progress == 50

    def test_NavQuizAttemptGetNextUserAttemptNo(self):
        user=auth.get_user(self.client)
        navAttempt=NavQuizAttempt.objects.get(id=1)
        nextNavAttempt=NavQuizAttempt.objects.create(user=user,
                                                finish_time=timezone.now(),
                                                score=0,
                                                user_attempt_no=0)


        next_user_attempt_no=nextNavAttempt.get_next_user_attempt_no()
        assert next_user_attempt_no==2

    def test_NavQuizAttemptGenerateNavQuiz(self):
        user=auth.get_user(self.client)

        navQuestion_one=NavQuestion.objects.get(id=1)
        navQuestion_two=NavQuestion.objects.get(id=2)
        navAttempt=NavQuizAttempt.objects.get(id=1 )

        navAttempt.generate_navQuiz()
        count_questions = NavAnswersSubmitted.objects.filter(attempt=navAttempt).aggregate(count=Count('id'))['count']
        assert count_questions == 5 # 5 is the current length of the navquiz

    def test_NavQuizAttemptCalculateScore(self):
        user=auth.get_user(self.client)

        navQuestion_one=NavQuestion.objects.get(id=1)
        navQuestion_two=NavQuestion.objects.get(id=2)
        navAttempt=NavQuizAttempt.objects.get(id=1)
        NavAnswersSubmitted.objects.create(user=user,
                                           article_submitted='1',
                                           question=navQuestion_one,
                                           attempt=navAttempt,
                                           start_time=timezone.now(),
                                           finish_time=timezone.now(),
                                           submitted_bool=True,
                                           correct_bool=True)
        NavAnswersSubmitted.objects.create(user=user,
                                           article_submitted='2',
                                           question=navQuestion_two,
                                           attempt=navAttempt,
                                           start_time=timezone.now(),
                                           finish_time=timezone.now(),
                                           submitted_bool=False,
                                           correct_bool=False)

        score = navAttempt.calculate_score()
        assert score == 50

    def test_NavQuizAttemptIsThereUnansweredQuestion(self):
        user=auth.get_user(self.client)

        navQuestion_one=NavQuestion.objects.get(id=1)
        navQuestion_two=NavQuestion.objects.get(id=2)
        navAttempt=NavQuizAttempt.objects.get(id=1)
        NavAnswersSubmitted.objects.create(user=user,
                                           article_submitted='1',
                                           question=navQuestion_one,
                                           attempt=navAttempt,
                                           start_time=timezone.now(),
                                           finish_time=timezone.now(),
                                           submitted_bool=True,
                                           correct_bool=True)
        NavAnswersSubmitted.objects.create(user=user,
                                           article_submitted='2',
                                           question=navQuestion_two,
                                           attempt=navAttempt,
                                           start_time=timezone.now(),
                                           finish_time=timezone.now(),
                                           submitted_bool=False,
                                           correct_bool=False)

        assert navAttempt.isThereUnAnsweredQuestion() == True

    def test_NavQuizAttemptGetNextQuestion(self):
        user=auth.get_user(self.client)

        navQuestion_one=NavQuestion.objects.get(id=1)
        navQuestion_two=NavQuestion.objects.get(id=2)
        navAttempt=NavQuizAttempt.objects.get(id=1)
        answer_submit1=NavAnswersSubmitted.objects.create(user=user,
                                           article_submitted='1',
                                           question=navQuestion_one,
                                           attempt=navAttempt,
                                           start_time=timezone.now(),
                                           finish_time=timezone.now(),
                                           submitted_bool=True,
                                           correct_bool=True)
        answer_submit2=NavAnswersSubmitted.objects.create(user=user,
                                           article_submitted='2',
                                           question=navQuestion_two,
                                           attempt=navAttempt,
                                           start_time=timezone.now(),
                                           finish_time=timezone.now(),
                                           submitted_bool=False,
                                           correct_bool=False)
        result = navAttempt.getNextQuestionAttempt()
        assert result == answer_submit2

    def test_NavQuizAttemptFinishAttempt(self):
        user=auth.get_user(self.client)

        navQuestion_one=NavQuestion.objects.get(id=1)
        navQuestion_two=NavQuestion.objects.get(id=2)
        navAttempt=NavQuizAttempt.objects.get(id=1)
        answer_submit1=NavAnswersSubmitted.objects.create(user=user,
                                           article_submitted='1',
                                           question=navQuestion_one,
                                           attempt=navAttempt,
                                           start_time=timezone.now(),
                                           finish_time=timezone.now(),
                                           submitted_bool=True,
                                           correct_bool=True)

        navAttempt.finishAttempt()
        assert navAttempt.submitted_bool == True

class NavQuizAttemptModelTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.client.login(username='test_UserProfile', password='abc123')
        
    @classmethod
    def setUpTestData(cls):
        cls.user=CustomUser.objects.create_user('test_UserProfile',
                                            email='a@a.net',
                                            password='abc123')
        cls.user.save()

        navQuestion1 = NavQuestion.objects.create(text='NavQuestion1 name')
        navQuestion2 = NavQuestion.objects.create(text='NavQuestion2 name')
        navQuestion3 = NavQuestion.objects.create(text='NavQuestion3 name')
        navQuestion4 = NavQuestion.objects.create(text='NavQuestion4 name')
        navQuestion5 = NavQuestion.objects.create(text='NavQuestion5 name')
        navQuestion6 = NavQuestion.objects.create(text='NavQuestion6 name')
        navAnswer1 = NavAnswer.objects.create(question=navQuestion1,
                                              mpep_chapter=1,
                                              mpep_article=1,
                                              mpep_location='1',
                                              section_title='navAnswer1')
        navAnswer2 = NavAnswer.objects.create(question=navQuestion2,
                                              mpep_chapter=2,
                                              mpep_article=2,
                                              mpep_location='2',
                                              section_title='navAnswer2')
        navAnswer3 = NavAnswer.objects.create(question=navQuestion3,
                                              mpep_chapter=3,
                                              mpep_article=3,
                                              mpep_location='3',
                                              section_title='navAnswer3')

        navAttempt=NavQuizAttempt.objects.create(user=cls.user,
                                                 finish_time=timezone.now(),
                                                 score=0,
                                                 user_attempt_no=1)
        answer_submit1=NavAnswersSubmitted.objects.create(user=cls.user,
                                            article_submitted='1',
                                            question=navQuestion1,
                                            attempt=navAttempt,
                                            start_time=timezone.now(),
                                            finish_time=timezone.now(),
                                            submitted_bool=False,
                                            correct_bool=False)
        answer_submit2=NavAnswersSubmitted.objects.create(user=cls.user,
                                           article_submitted='F',
                                           question=navQuestion2,
                                           attempt=navAttempt,
                                           start_time=timezone.now(),
                                           finish_time=timezone.now(),
                                           submitted_bool=False,
                                           correct_bool=False)



    def test_NavQuizAttemptSaveUserAnswerTrue(self):
        user=auth.get_user(self.client)
        navAttempt=NavQuizAttempt.objects.get(id=1)

        answer_submit1=NavAnswersSubmitted.objects.get(id=1)
        answer_submit1.save_user_answer('1')

        assert answer_submit1.correct_bool == True


    def test_NavQuizAttemptSaveUserAnswerFalse(self):
        user=auth.get_user(self.client)
        navAttempt=NavQuizAttempt.objects.get(id=1)

        answer_submit1=NavAnswersSubmitted.objects.get(id=2)
        answer_submit1.save_user_answer('F')

        assert answer_submit1.correct_bool == False
