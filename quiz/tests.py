from django.http import HttpRequest, HttpResponse
from django.test import Client, TestCase
from django.urls import reverse

from quiz.views import HomePageView, IndexView
from quiz.models import Quiz
# Create your tests here.


class HomePageTest(TestCase):

    def test_home_page_is_about_patent_bar(self):
        request = HttpRequest()

        response = HomePageView(request)

        self.assertTrue(response.content.startswith(b'<html>'))
        self.assertIn(b'<title>Patent-Bar</title>', response.content)
        self.assertTrue(response.content.endswith(b'</html>'))


class QuizIndexTest(TestCase):

    def test_quiz_page_has_html(self):
        response = self.client.get('/quiz/')
        self.assertTemplateUsed(response, 'quiz/index.html')


    def test_quiz_page_has_links_to_a_quiz(self):
        response = self.client.get('/quiz/')
        self.assertIn(b'<a href=', response.content)


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

    def test_quiz_get_context_data_contains_one_object(self):
        x = 1 # initial quiz
        path = reverse('quiz:detail', args=(x,))
        response = self.client.get(path)
        #Quiz.objects.get(id=x) == QuizDetailView

    def test_quiz_detail_html_displays_quiz_title(self):
        x = 1 # initial quiz
        path = reverse('quiz:detail', args=(x,))
        response = self.client.get(path)
        print(response)
        print(Quiz.objects.get(id=x).title)
        quiz_title = Quiz.objects.get(id=x).title
        print(quiz_title)
        self.assertIn(quiz_title.encode('utf-8'), response.content)


#class QuizModelTest(TestCase):

#    def test_quiz_model
