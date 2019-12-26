#import unittest
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

class NewVisitorTest(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_accessing_home(self):
        self.browser.get(self.live_server_url)

        self.assertIn('Patent-Bar', self.browser.title)

    def test_accessing_quiz_list(self):
        # Bob has heard about quiz app
        # He goes to its homepage
        self.browser.get('http://localhost:8000/quiz')

        # He notices the Browser title is patentbar
        self.assertIn('Patent-Bar', self.browser.title)

        # He notices the browser heading is Quiz
        header = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Quiz',header.text)

        # He sees a list in the body
        list = self.browser.find_element_by_tag_name('ul')
        self.assertIn('This is an item on the list', list.text)

        # Each item in the list is a link
        list_items = self.browser.find_elements_by_tag_name('li')
        for item in list_items:
            link = item.find_element_by_tag_name('a')

        # This page is about the quiz he selected

    def test_accessing_quiz_details(self):

        Quiz.objects.create(id=1, title = "Testing Quiz 1")
        Quiz.objects.create(id=2, title = "Testing Quiz 2")

        # He goes to the first test and notices the header of the page is
        # the title of the quiz
        x = 1 # first quiz
        self.browser.get('http://localhost:8000/quiz/%x/')
        header = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Quiz 1', header.text)

        # He then checks the second quiz
        x = 2 # second quiz
        self.browser.get('http://localhost:8000/quiz/%x/')
        header = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Quiz 2', header.text)


        self.fail('Finish this test')
