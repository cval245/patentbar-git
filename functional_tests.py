import unittest
from selenium import webdriver

class NewVisitorTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_accessing_quiz_list(self):
        # Bob has heard about quiz app
        # He goest to its homepage
        self.browser.get('http://localhost:8000/quiz')

        # He notices the Browser heading is patentbar
        self.assertIn('Patent-Bar', self.browser.title)

if __name__ == '__main__':
    unittest.main(warnings='ignore')
