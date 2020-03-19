from django.http import HttpRequest, HttpResponse
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from quiz.forms import AnswerForm

from userProfile.models import AnswersSubmitted, QuizAttempt
from quiz.models import Answer, Question, Quiz
from users.models import CustomUser

from quiz.views import HomePageView, IndexView
# Create your tests here.


class HomePageTest(TestCase):

    def test_home_page_is_about_patent_bar(self):
        request = HttpRequest()

        response = HomePageView(request)

        self.assertTrue(response.content.startswith(b'<html>'))
        self.assertIn(b'<title>Patent-Bar</title>', response.content)
        self.assertIn(b'</html>', response.content)

    def test_home_page_has_link_to_quiz(self):
        response = self.client.get('/')
        self.assertIn(b'<a href="/quiz/"', response.content)

    def test_home_page_has_link_to_login(self):
        response = self.client.get('/')
        self.assertIn(b'<a href="/account/login/"', response.content)

    def test_home_page_has_link_to_signup(self):
        response = self.client.get('/')
        self.assertIn(b'<a href="/account/signup/"', response.content)

class QuizIndexTest(TestCase):

    def setUp(self):
        Quiz.objects.create(id=1, title = "Testing Quiz 1")
        Quiz.objects.create(id=2, title = "Testing Quiz 2")
        self.client = Client()


    def test_quiz_page_has_html(self):
        response = self.client.get('/quiz/')
        self.assertTemplateUsed(response, 'quiz/index.html')


    def test_quiz_page_has_links(self):
        response = self.client.get('/quiz/')
        self.assertIn(b'<a href=', response.content)

    def test_quiz_page_index_view_passes_quiz_title_in_context(self):
        response = self.client.get('/quiz/')
        self.assertQuerysetEqual(response.context['quiz'],
                                 map(repr, Quiz.objects.all()))


class QuizDetailView(TestCase):

    def setUp(self):
        Quiz.objects.create(id=1, title = "Testing Quiz 1")
        Quiz.objects.create(id=2, title = "Testing Quiz 2")
        self.client = Client()
        user=CustomUser.objects.create_user('test_UserProfile',
                                             email='a@a.net',
                                             password='abc123')
        user.save()
        self.client.login(username='test_UserProfile', password='abc123')

    def test_quiz_detail_has_html(self):
        x = 1 # initial quiz
        path = reverse('quiz:detail', args=(x,))
        response = self.client.get(path)
        self.assertTemplateUsed(response, 'quiz/detail.html')

    def test_quiz_form_passed_in_context(self):
        quiz_id = 1 # initial quiz
        path = reverse('quiz:detail', args=(quiz_id,))
        response = self.client.get(path)
        self.assertIn('form', response.context)

        # This makes sure the form is an AnswerForm class
        context_form = response.context['form']
        self.assertIn('QuizStartForm', context_form.__class__.__name__)

    def test_quiz_detail_get_form_displays_quiz_choices(self):
        quiz_id = 1
        path=(reverse('quiz:detail', args=(quiz_id,)))
        response = self.client.get(path)

    def test_quiz_detail_saves_to_model_QuizAttempt(self):
        quiz_id = 1
        path = reverse('quiz:detail', args=(quiz_id,))
        response = self.client.post(path, {'quizzes':quiz_id})
        saved_attempt = QuizAttempt.objects.filter(id=1)
        self.assertEqual(saved_attempt.quiz.id, quiz_id)

class QuestionModelTest(TestCase):
    def setUp(self):
        question_id = 1
        answer_id = 1
        answer_id_two = 2
        quiz_id = 1
        Quiz.objects.create(id=quiz_id, title = "Testing Quiz 1")
        Question.objects.create(id=question_id,
                                quiz=Quiz.objects.get(id=quiz_id),
                                text = "Testing Question 1")

    def test_foreign_key_to_quiz(self):
        for count, question in enumerate(Question.objects.all(), start=1):
            Question.objects.get(id=count).quiz.id



class AnswerModelTest(TestCase):
    def setUp(self):
        question_id = 1
        answer_id = 1
        answer_id_two = 2
        quiz_id = 1
        Quiz.objects.create(id=quiz_id, title = "Testing Quiz 1")
        Question.objects.create(id=question_id,
                                quiz=Quiz.objects.get(id=quiz_id),
                                text = "Testing Question 1")
        Answer.objects.create(id=answer_id,
                              question=Question.objects.get(id=question_id),
                              text="Question 1 Answer A",
                              correct_bool=True)
        Answer.objects.create(id=answer_id_two,
                              question=Question.objects.get(id=question_id),
                              text="Question 1 Answer B",
                              correct_bool=False)

    def test_foreign_key_to_quiz(self):
        for count, answer in enumerate(Answer.objects.all(), start=1):
            self.fail("Need to finish this test")

class QuizQuestionTest(TestCase):
    def setUp(self):

        user=CustomUser.objects.create_user('test_UserProfile',
                                             email='a@a.net',
                                             password='abc123')
        user.save()
        self.client.login(username='test_UserProfile', password='abc123')

        question_id = 1
        question_id_two = 2
        answer_id = 1
        answer_id_two = 2
        answer_id_three = 3
        answer_id_four = 4
        quiz_id = 1
        Quiz.objects.create(id=quiz_id, title = "Testing Quiz 1")
        Question.objects.create(id=question_id,
                                quiz=Quiz.objects.get(id=quiz_id),
                                text = "Testing Question 1")
        Answer.objects.create(id=answer_id,
                              question=Question.objects.get(id=question_id),
                              text="Question 1 Answer A",
                              correct_bool=True)
        Answer.objects.create(id=answer_id_two,
                              question=Question.objects.get(id=question_id),
                              text="Question 1 Answer B",
                              correct_bool=False)

        Question.objects.create(id=question_id_two,
                                quiz=Quiz.objects.get(id=quiz_id),
                                text = "Testing Question 1")
        Answer.objects.create(id=answer_id_three,
                              question=Question.objects.get(id=question_id_two),
                              text="Question 1 Answer A",
                              correct_bool=True)
        Answer.objects.create(id=answer_id_four,
                              question=Question.objects.get(id=question_id_two),
                              text="Question 1 Answer B",
                              correct_bool=False)

    def test_quiz_question_has_html(self):
        quiz_id = 1 # initial quiz
        question_id = 1 # initial question
        attempt_id = 1
        path = reverse('quiz:question', args=(quiz_id,
                                              attempt_id, question_id))
        response = self.client.get(path)
        self.assertTemplateUsed(response, 'quiz/question.html')

    def test_quiz_form_passed_in_context(self):
        quiz_id = 1 # initial quiz
        question_id = 1 # initial question
        attempt_id = 1
        path = reverse('quiz:question', args=(quiz_id, attempt_id,
                                              question_id))
        response = self.client.get(path)
        self.assertIn('form', response.context)

        # This makes sure the form is an AnswerForm class
        context_form = response.context['form']
        self.assertIn('AnswerForm', context_form.__class__.__name__)

    def test_submitted_answer_saved_to_AnswersSubmitted_POST(self):
        user_id = 1
        quiz_id = 1 # initial quiz
        question_id = 1 # initial question
        answer_id = 1
        attempt_id = 1


        path = reverse('quiz:question', args=(quiz_id, attempt_id,
                                              question_id))
        QUESTION = Question.objects.get(id=question_id)
        ANSWER = Answer.objects.get(id=answer_id)

        self.client.post(path, {'choice':answer_id})
        selected_answer =AnswersSubmitted.objects.get(answer__exact=ANSWER,
                                           question__exact = QUESTION)
        self.assertEqual(ANSWER, selected_answer.answer)


    def test_submitted_answer_redirects_to_next_Question(self):
        user_id = 1
        quiz_id = 1 # initial quiz
        question_id = 1 # initial question
        question_id_two = 2
        answer_id = 1
        attempt_id = 1

        path = reverse('quiz:question', args=(quiz_id, attempt_id,
                                              question_id))
        QUESTION = Question.objects.get(id=question_id)
        ANSWER = Answer.objects.get(id=answer_id)

        response = self.client.post(path, {'choice':answer_id})
        self.assertEqual(response.get('location'),
                         reverse('quiz:question', args=(quiz_id, attempt_id,
                                                        question_id_two)))


class StartQuizFormTest(TestCase):
    def setUp(self):
        question_id = 1
        answer_id = 1
        answer_id_two = 2
        quiz_id = 1
        Quiz.objects.create(id=quiz_id, title = "Testing Quiz 1")
        Question.objects.create(id=question_id,
                                quiz=Quiz.objects.get(id=quiz_id),
                                text = "Testing Question 1")
        Answer.objects.create(id=answer_id,
                              question=Question.objects.get(id=question_id),
                              text="Question 1 Answer A",
                              correct_bool=True)
        Answer.objects.create(id=answer_id_two,
                              question=Question.objects.get(id=question_id),
                              text="Question 1 Answer B",
                              correct_bool=False)

    #def test_start_quiz_form

class QuizAnswerFormTest(TestCase):

    def setUp(self):
        question_id = 1
        answer_id = 1
        answer_id_two = 2
        quiz_id = 1
        Quiz.objects.create(id=quiz_id, title = "Testing Quiz 1")
        Question.objects.create(id=question_id,
                                quiz=Quiz.objects.get(id=quiz_id),
                                text = "Testing Question 1")
        Answer.objects.create(id=answer_id,
                              question=Question.objects.get(id=question_id),
                              text="Question 1 Answer A",
                              correct_bool=True)
        Answer.objects.create(id=answer_id_two,
                              question=Question.objects.get(id=question_id),
                              text="Question 1 Answer B",
                              correct_bool=False)


    def test_form_renders_radio_buttons(self):
        form = AnswerForm()
        for field in form:
            widget_desired = forms.widgets.Textarea
            widget_displayed = field.field.widget
            #self.assertIn(str(widget_desired), str(widget_displayed))
        ## no idea how to run this testing
        self.fail()


    def test_form_for_error_message(self):
        form_data = {'answer':''}
        form = AnswerForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['choice'], ["Please select an answer"])

class EndOfQuizPageTest(TestCase):
    def setUp(self):
        question_id = 1
        answer_id = 1
        answer_id_two = 2
        quiz_id = 1
        Quiz.objects.create(id=quiz_id, title = "Testing Quiz 1")
        Question.objects.create(id=question_id,
                                quiz=Quiz.objects.get(id=quiz_id),
                                text = "Testing Question 1")
        Answer.objects.create(id=answer_id,
                              question=Question.objects.get(id=question_id),
                              text="Question 1 Answer A")
        Answer.objects.create(id=answer_id_two,
                              question=Question.objects.get(id=question_id),
                              text="Question 1 Answer B")

    def test_end_of_quiz_uses_template(self):
        quiz_id = 1 # initial quiz
        attempt_id = 1
        path = reverse('quiz:endQuiz', args=(quiz_id,attempt_id))
        response = self.client.get(path)
        self.assertTemplateUsed(response, 'quiz/endQuiz.html')

    #def test_end_of_quiz_displays_(self):


