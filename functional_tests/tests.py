import time
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from quiz.models import Answer, Quiz

class NewVisitorTest(LiveServerTestCase):

    def setUp(self):
        Quiz.objects.create(id=1, title="Functional Testing Quiz 1")
        Quiz.objects.create(id=2, title="Functional Testing Quiz 2")
        Answer.objects.create(id=1, quiz=1, text="Quiz 1 Answer A")
        Answer.objects.create(id=2, quiz=2, text="Quiz 1 Answer A")
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_accessing_home(self):
        self.browser.get(self.live_server_url)

        self.assertIn('Patent-Bar', self.browser.title)

    def test_accessing_quiz_list(self):
        # Bob has heard about quiz app
        # He goes to its homepage
        self.browser.get(self.live_server_url + '/quiz')

        # He notices the Browser title is patentbar
        self.assertIn('Patent-Bar', self.browser.title)

        # He notices the browser heading is Quiz
        header = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Quiz',header.text)

        # He notices there is a list
        list_test = self.browser.find_element_by_tag_name('ul')

        # Each item in the list is a link that has a title that corresponds
        # to the title of the quiz
        list_items = self.browser.find_elements_by_tag_name('li')
        for count, item in enumerate(list_items, start=1):
            element = item.find_element_by_tag_name('a')
            self.assertEquals(Quiz.objects.get(id=count).title, element.text)

        # Each item in the list is a link that goes to somewhere else
        ## The below link explains where I got the code. I added this to get
        ## over a NoSuchElementException Error.  It is storying the links
        ## prior to clicking on them
        ## https://stackoverflow.com/questions/24775988/how-to-navigate-to-a-
        ## new-webpage-in-selenium
        elements = self.browser.find_elements_by_tag_name('a')
        links = []
        for i in range(len(elements)):
            links.append(elements[i].get_attribute('href'))
        for link in links:
            print(link)
            self.browser.get(link)


    def test_accessing_quiz_details(self):

        # He goes to the first test and notices the header of the page is
        # the title of the quiz
        quiz_no = 1 # first quiz
        self.browser.get(self.live_server_url + '/quiz/{}'.format(quiz_no))
        header = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Functional Testing Quiz 1', header.text)

        # He then checks the second quiz and notices the header of the page
        # is the title of the second quiz
        quiz_no = 2 # second quiz
        self.browser.get(self.live_server_url + '/quiz/{}'.format(quiz_no))
        header = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Functional Testing Quiz 2', header.text)

        # There is a button which allows him to start the quiz.
        self.fail('Finish this test')

    def test_starting_quiz_page(self):

        # He starts the exam and he sees a question
        quiz_no = 1 # first quiz
        self.browser.get(self.live_server_url +
                         '/quiz/{}/start'.format(quiz_no))
        header = self.browser.find_element_by_tag_name('h1')
        self.assertEquals(Quiz.objects.get(id=quiz_no).title, header.text)

        quiz_no = 1 # first quiz
        self.browser.get(self.live_server_url +
                         '/quiz/{}/start'.format(quiz_no))
        header = self.browser.find_element_by_tag_name('h1')
        self.assertEquals(Quiz.objects.get(id=quiz_no).title, header.text)

        # He sees a different selection of answers
        


        # The answers are displayed in radiobuttons

        # There is a submit button that will save the response

        ## This is a temporary option
        # Upon the pressing of the button he is taken to a success page
        # containing the answer he selected.

        # The selected choice is saved.
        self.fail('Finish this at long last')
