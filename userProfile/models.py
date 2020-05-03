from django.db import models
from quiz.models import Answer, Question, Quiz
from navquiz.models import NavQuestion, NavAnswer
from django.db.models import Count

import datetime
# Create your models here.

class QuizAttempt(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    finish_time = models.DateTimeField()
    score = models.DecimalField(max_digits=5, decimal_places=2)
    time_taken = models.DurationField(default=datetime.timedelta())
    submitted_bool = models.BooleanField(default=False)
    user_attempt_no = models.IntegerField()

    def update_or_add_answer(self, question, answer):
        quiz=self.quiz
        # answersubmitted exist
        if AnswersSubmitted.objects.filter(attempt=self,
                                           question=question).exists():
            old_answer=AnswersSubmitted.objects.get(attempt=self,
                                                    question=question)
            old_answer.setAnswer(answer)

        # answersubmitted does not exist
        else:
            # Create a new entry
            if self.submitted_bool == False:
                AnswersSubmitted.objects.create(user=self.user,
                                                question=question,
                                                answer=answer,attempt=self)

    def calculate_score(self):
        quiz=self.quiz
        quiz_questions=Question.objects.filter(quiz=quiz)
        answers = Answer.objects.filter(question__in=quiz_questions)
        results=AnswersSubmitted.objects.filter(attempt=self)
        selected_answers=Answer.objects.filter(answerssubmitted__in=results)
        correct_answers=selected_answers.filter(correct_bool=True).count()
        all_answers=selected_answers.count()
        score = correct_answers / all_answers * 100
        return score

    def set_score(self):
        if self.submitted_bool == False:
            self.score = self.calculate_score()
            self.save()

    def list_time_taken(self):
        days = self.time_taken.days
        hours = self.time_taken.seconds//3600
        minutes = (self.time_taken.seconds//60)%60
        seconds = self.time_taken.seconds%60
        return {'days':days, 'hours':hours, 'minutes':minutes,
                'seconds':seconds}

    def get_next_user_attempt_no(self, user, quiz):
        quizzes=QuizAttempt.objects.filter(user=user, quiz=quiz)

        # if the queryset exists then get next iterate user_attempt_no
        if quizzes.exists():
            last_attempt = quizzes.order_by('user_attempt_no').last()
            next_user_attempt_no=last_attempt.user_attempt_no + 1
        else:
            next_user_attempt_no=1
        return next_user_attempt_no

    # Calculates the user's progress through the test for that attempt
    def progress(self, user, quiz):

        # calculates total number of questions
        total_questions=Question.objects.filter(quiz=quiz).aggregate(Count('id'))
        num_total_questions=total_questions.get('id__count')
        #calculates answered questions
        answered_questions=AnswersSubmitted.objects.filter(user=user,attempt=self).aggregate(Count('question'))
        num_answered_questions=answered_questions.get('question__count')

        # returns progress out of 100
        progress = num_answered_questions / num_total_questions * 100
        return progress

class AnswersSubmitted(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE)

    

    def setAnswer(self, answer):
        if self.attempt.submitted_bool == False:
            self.answer = answer
            self.save()

    #determines if this is the last question returns True/False
    def isLastUnAnsweredQuestion(self):
        attempt=self.attempt
        quiz=self.attempt.quiz
        answered_questions = AnswersSubmitted.objects.filter(attempt=attempt)
        questions=Question.objects.filter(quiz=quiz)

        count_answered=answered_questions.aggregate(count=Count('id'))
        count_questions=questions.aggregate(count=Count('id'))
        if count_answered == count_questions:
            return True
        else:
            return False

    def getFirstUnansweredQuestion(self):
        attempt=self.attempt
        quiz=self.attempt.quiz
        if self.isLastUnAnsweredQuestion() == True:
            return None
        elif self.isLastUnAnsweredQuestion() == False:
            answered_questions=AnswersSubmitted.objects.filter(attempt=attempt).values('question')
            questions=Question.objects.filter(quiz=quiz)
            unanswered_questions=questions.exclude(id__in=answered_questions)
            next_question=unanswered_questions.order_by('id').first()
            return next_question

    def getLastUnansweredQuestion(self):
        attempt=self.attempt
        quiz=self.attempt.quiz
        if self.isLastUnAnsweredQuestion() == True:
            return None
        elif self.isLastUnAnsweredQuestion() == False:
            answered_questions=AnswersSubmitted.objects.filter(attempt=attempt).values('question')
            questions=Question.objects.filter(quiz=quiz)
            unanswered_questions=questions.exclude(id__in=answered_questions)
            next_question=unanswered_questions.order_by('id').last()
            return next_question


    def getNextQuestion(self):
        attempt=self.attempt
        quiz=self.attempt.quiz
        question = self.question
        quiz_questions = Question.objects.filter(quiz=quiz).order_by('id')
        # if there are no more unanswered questions return None
        if self.isLastUnAnsweredQuestion() == True:
            return None
        # if there is a next question (by id) (this is not the last
        # unanswered question)
        elif question.id < self.getLastUnansweredQuestion().id:
            question = quiz_questions.filter(id__gt=question.id).first()
            return question
        # if there is not a next question (recycle from top)
        elif question.id >= self.getLastUnansweredQuestion().id:
            question = self.getFirstUnansweredQuestion()
            return question
        return '404'

class NavQuizAttempt(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    finish_time = models.DateTimeField()
    score = models.DecimalField(max_digits=5, decimal_places=2)
    time_taken = models.DurationField(default=datetime.timedelta())
    submitted_bool = models.BooleanField(default=False)
    user_attempt_no = models.IntegerField()

    def list_time_taken(self):
        days = self.time_taken.days
        hours = self.time_taken.seconds//3600
        minutes = (self.time_taken.seconds//60)%60
        seconds = self.time_taken.seconds%60
        return {'days':days, 'hours':hours, 'minutes':minutes,
                'seconds':seconds}

    def avg_time(self):
        num_questions = NavQuizAttempt.objects.filter(
            user_attempt_no = self.user_attempt_no).aggregate(count=Count('id'))
        num_questions = NavAnswersSubmitted.objects.filter(attempt=self.id).aggregate(count=Count('id'))
        average_time = self.time_taken.seconds / num_questions['count']
        return average_time

    def calc_composite_score(self):
        avg_time=self.avg_time()
        if avg_time < 60.0:
            time_score = 100
        elif avg_time > 60.0 and avg_time < 120.0:
            time_score = 70
        elif avg_time > 120.0 and avg_time < 180.0:
            time_score = 20
        elif avg_time > 180.0:
            time_score = 20

        comp_score = (self.score + time_score) / 2
        return comp_score

class NavAnswersSubmitted(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    article_submitted = models.CharField(max_length=50)
    question = models.ForeignKey(NavQuestion, on_delete=models.CASCADE)
    attempt = models.ForeignKey(NavQuizAttempt, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    finish_time = models.DateTimeField()
    time_taken = models.DurationField(default=datetime.timedelta())
    correct_bool = models.BooleanField(default=False)
    submitted_bool = models.BooleanField(default=False)

    def list_time_taken(self):
        days = self.time_taken.days
        hours = self.time_taken.seconds//3600
        minutes = (self.time_taken.seconds//60)%60
        seconds = self.time_taken.seconds%60
        return {'days':days, 'hours':hours, 'minutes':minutes,
                'seconds':seconds}
