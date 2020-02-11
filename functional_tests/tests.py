import time
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from quiz.models import Answer, Question, Quiz
from users.models import CustomUser

class VisitorAccountsTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_title_on_accounts_page(self):
        self.browser.get(self.live_server_url)
        self.assertIn('Patent-Bar', self.browser.title + '/account')

    def test_account_text_on_accounts_page(self):
        self.browser.get(self.live_server_url + '/account')
        header = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Login', header.text)

    # The logged in user sees his username
    def test_username_shown_on_dashboard(self):
        password = 'abc123'
        user = CustomUser.objects.create_user('testUserBob','bob@bob.com'
                                              , password)
        user.save()
        self.login_with_test_default(user, password)

        header = self.browser.find_element_by_tag_name('p')
        self.assertIn(user.username, header.text)

    def login_with_test_default(self, user, password):

        self.browser.get(self.live_server_url + '/account/')
        username_field = self.browser.find_element_by_css_selector('form input[name="username"]')
        password_field = self.browser.find_element_by_css_selector('form input[name="password"]')
        username_field.send_keys(user.username)
        password_field.send_keys(password)

        submit = self.browser.find_element_by_css_selector('form input[type="submit"]')
        submit.click()

class VisitorSignUpTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_title_on_signup_page(self):
        self.browser.get(self.live_server_url)
        self.assertIn('Patent-Bar', self.browser.title + '/account/signup')

    def test_signup_text_on_signup_page(self):
        self.browser.get(self.live_server_url + '/account/signup')
        header = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Sign Up', header.text)

    def test_form_on_signup_page(self):
        self.browser.get(self.live_server_url + '/account/signup')
        form = self.browser.find_element_by_tag_name('form')
        self.assertIn('post', form.get_attribute("method"))

class VisitorLoginTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_title_on_login_page(self):
        self.browser.get(self.live_server_url)
        self.assertIn('Patent-Bar', self.browser.title + '/account/login')

    def test_login_text_on_login_page(self):
        self.browser.get(self.live_server_url + '/account/login')
        header = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Login', header.text)

class NewVisitorTest(LiveServerTestCase):

    def setUp(self):
        question_id = 1
        answer_id = 1
        answer_id_two = 2
        quiz_id = 1
        Quiz.objects.create(id=quiz_id, title = "Functional Testing Quiz 1")
        Quiz.objects.create(id=2, title="Functional Testing Quiz 2")
        Question.objects.create(id=question_id,
                                quiz=Quiz.objects.get(id=quiz_id),
                                text = "Testing Question 1")
        Answer.objects.create(id=answer_id,
                              question=Question.objects.get(id=question_id),
                              text="Question 1 Answer A")
        Answer.objects.create(id=answer_id_two,
                              question=Question.objects.get(id=question_id),
                              text="Question 1 Answer B")

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
        self.assertIn('Quiz', header.text)

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
        # select a quiz
        quiz_no = 1 # first quiz
        self.browser.get(self.live_server_url + '/quiz/{}'.format(quiz_no))
        header = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Select a Quiz', header.text)

        # He then checks the second quiz and notices the header of the page
        # is the title of the second quiz
        quiz_no = 2 # second quiz
        self.browser.get(self.live_server_url + '/quiz/{}'.format(quiz_no))
        header = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Select a Quiz', header.text)

        # There is a button with the name to start the quiz.
        input_button = self.browser.find_element_by_name('start')
        self.assertIn('Start Quiz', input_button.get_attribute("value"))

        # There is a form
        form = self.browser.find_element_by_tag_name('form')
        self.assertIn('post', form.get_attribute("method"))

    def test_quiz_question_page(self):

        # He starts the exam and he sees a question
        quiz_no = 1 # first quiz
        question_id = 1
        self.browser.get(self.live_server_url +
                         '/quiz/{}/question{}'.format(quiz_no, question_id))
        header = self.browser.find_element_by_tag_name('h1')

        ## Commented out because form replaced question text
        #self.assertEquals(Question.objects.get(id=question_id).text,
        #                  header.text)


        # He sees a form with a different selection of answers these answers
        # correspond to the answers to each question.
        answers = Answer.objects.filter(question=question_id)
        displayed_list = self.browser.find_elements_by_tag_name('li')

        # if there is an error, maybe there is an extra <li> somewhere
        for i, answer in enumerate(answers,):
            self.assertIn(answer.text, displayed_list[i].text)

        # The answers are displayed in radiobuttons

        # There is a submit button that will save the response

        ## This is a temporary option
        # Upon the pressing of the button he is taken to a success page
        # containing the answer he selected.

        # The selected choice is saved.
        self.fail('Finish this at long last')
