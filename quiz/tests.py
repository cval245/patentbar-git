from django.http import HttpRequest, HttpResponse
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from quiz.forms import AnswerForm

from userProfile.models import AnswersSubmitted, QuizAttempt
from quiz.models import Answer, Question, Quiz

from quiz.views import HomePageView, IndexView
# Create your tests here.


class HomePageTest(TestCase):

    def test_home_page_is_about_patent_bar(self):
        request = HttpRequest()

        response = HomePageView(request)

        self.assertTrue(response.content.startswith(b'<html>'))
        self.assertIn(b'<title>Patent-Bar</title>', response.content)
        self.assertTrue(response.content.endswith(b'</html>'))


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
        print("Look at this !", QuizAttempt.objects.all())
        saved_attempt = QuizAttempt.objects.get(id=1)
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
                              text="Question 1 Answer A")
        Answer.objects.create(id=answer_id_two,
                              question=Question.objects.get(id=question_id),
                              text="Question 1 Answer B")

    def test_foreign_key_to_quiz(self):
        for count, answer in enumerate(Answer.objects.all(), start=1):
            print(Answer.objects.get(id=count).question.quiz)
            self.fail("Need to finish this test")

class QuizQuestionTest(TestCase):
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

    def test_quiz_question_has_html(self):
        quiz_id = 1 # initial quiz
        question_id = 1 # initial question
        path = reverse('quiz:question', args=(quiz_id,question_id))
        response = self.client.get(path)
        self.assertTemplateUsed(response, 'quiz/question.html')

    def test_quiz_form_passed_in_context(self):
        quiz_id = 1 # initial quiz
        question_id = 1 # initial question
        path = reverse('quiz:question', args=(quiz_id,question_id))
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

        path = reverse('quiz:question', args=(quiz_id, question_id))
        QUESTION = Question.objects.get(id=question_id)
        ANSWER = Answer.objects.get(id=answer_id)

        self.client.post(path, {'choice':answer_id})
        selected_answer =AnswersSubmitted.objects.get(answer__exact=ANSWER,
                                           question__exact = QUESTION)
        self.assertEqual(ANSWER, selected_answer.answer)

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
                              text="Question 1 Answer A")
        Answer.objects.create(id=answer_id_two,
                              question=Question.objects.get(id=question_id),
                              text="Question 1 Answer B")

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
                              text="Question 1 Answer A")
        Answer.objects.create(id=answer_id_two,
                              question=Question.objects.get(id=question_id),
                              text="Question 1 Answer B")


    def test_form_renders_radio_buttons(self):
        form = AnswerForm()
        for field in form:
            print(field.field.widget)
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
