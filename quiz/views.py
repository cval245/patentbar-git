from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Value, BooleanField
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .forms import  AnswerForm
from .models import Answer, Question, Quiz
from userProfile.models import AnswersSubmitted, QuizAttempt
from datetime import datetime
# Create your views here.

class HomePageView(generic.TemplateView):
    template_logged_in = 'homePage_logged_in.html'
    template_logged_out = 'homePage_logged_out.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, self.template_logged_in,
                          {'username':request.user})
        else:
            return render(request, self.template_logged_out)

class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'quiz/index.html'
    context_object_name = 'quiz'
    login_url = '/account/login/'
    redirect_field_name = 'redirect_to'

    def get_queryset(self):
        """Return all the quizzes"""
        return Quiz.objects.order_by('title')

class QuizDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'quiz/detail.html'
    model = Quiz
    login_url = '/account/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'username':request.user})


    def post(self, request, *args, **kwargs):
        finish_time=datetime(2000, 1, 1, 0, 0, 0, 0) # default placeholder
        score=0 #default placeholder
        quiz_id = kwargs.pop('pk')
        quiz = Quiz.objects.get(id=quiz_id)

        attempt=QuizAttempt.objects.create(user=request.user, quiz=quiz,
                                           finish_time=timezone.now(),
                                           score=score, user_attempt_no=0)
        # get next user_attempt_no
        next_user_attempt_no = attempt.get_next_user_attempt_no(request.user,
                                                                quiz)
        attempt.user_attempt_no = next_user_attempt_no
        attempt.save()
        first_question=Question.objects.filter(quiz=quiz).first()
        return HttpResponseRedirect(
                reverse('quiz:question',
                        kwargs={'question_id':first_question.id,
                                'pk':quiz.id,
                                'user_attempt_no':next_user_attempt_no}))

class QuestionView(LoginRequiredMixin, generic.CreateView):
    form_class = AnswerForm
    template_name = 'quiz/question.html'
    model = Question
    login_url = '/account/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        question_id = self.kwargs.pop('question_id')
        quiz_id = self.kwargs.pop('pk')
        quiz = Quiz.objects.get(id=quiz_id)
        quiz_questions=Question.objects.filter(quiz=quiz)
        user_attempt_no = self.kwargs.pop('user_attempt_no')
        attempt = QuizAttempt.objects.get(user=request.user,
                                          quiz=quiz,
                                          user_attempt_no=user_attempt_no)

        question = Question.objects.get(id=question_id)
        answer_selected = AnswersSubmitted.objects.filter(question=question,
                                                          attempt=attempt)
        # Determine if the next question is there, then move to it
        # After the final question is answered, does a passthrough to
        # look for unanswered questions. If there are none, it moves to
        # the submitquiz section
        results =AnswersSubmitted.objects.filter(question__in=quiz_questions,
                                                  attempt=attempt)
        answered_questions = results.values('question')
        unanswered_questions = quiz_questions.exclude(
            id__in=answered_questions)
        answered_questions=quiz_questions.filter(id__in=answered_questions)

        answered_questions = answered_questions.annotate(
            answered_bool=Value(True, BooleanField()))
        unanswered_questions = unanswered_questions.annotate(
            answered_bool=Value(False, BooleanField()))
        status_questions = answered_questions.union(unanswered_questions).order_by('id')
        # Prepopulates the form field, if the user already selected
        if answer_selected:
            answer_selected_id=answer_selected.get().answer.id
            form = self.form_class(request.GET or None, question=question_id,
                                   initial={'choice':answer_selected_id})

        else:
            form = self.form_class(request.GET or None, question=question_id)

        #progress=self.calculateProgress(request.user, quiz_questions,attempt)
        progress = attempt.progress(request.user, quiz)
        return render(request, self.template_name,
                      {'form':form, 'question':question,
                       'attempt':attempt,
                       'status_questions':status_questions,
                       'quiz':quiz, 'username':request.user,
                       'answered_questions':answered_questions,
                       'attempt':attempt, 'progress':progress})

    def post(self, request, *args, **kwargs):
        question_id = self.kwargs.pop('question_id')
        quiz_id = self.kwargs.pop('pk')
        quiz = Quiz.objects.get(id=quiz_id)
        user_attempt_no = self.kwargs.pop('user_attempt_no')

        attempt = QuizAttempt.objects.get(user=request.user,
                                          quiz=quiz,
                                          user_attempt_no=user_attempt_no)
        next_question_id = question_id + 1
        quiz = Quiz.objects.get(id=quiz_id)
        quiz_questions=Question.objects.filter(quiz=quiz)
        QUESTION = quiz_questions.get(id=question_id)
        form = self.form_class(request.POST, question=question_id)

        if form.is_valid():
            ANSWER = form.cleaned_data['choice']

            if attempt.submitted_bool == False:

                # determine if user already entered an answer for that questions
                # if so, then update the old answer.
                if AnswersSubmitted.objects.filter(user=request.user,
                                                   question=QUESTION,
                                                   attempt=attempt).exists():
                    old_answer=AnswersSubmitted.objects.get(
                        user=request.user,
                        question=QUESTION,
                        attempt=attempt)
                    old_answer.answer = ANSWER
                    old_answer.save()
                    submission=old_answer
                else:
                    submission=AnswersSubmitted.objects.create(
                        user=request.user,
                        question=QUESTION,
                        answer=ANSWER,
                        attempt=attempt)
                # Determine if the next question is there, then move to it
                # After the final question is answered, does a passthrough to
                # look for unanswered questions. If there are none, it moves to
                # the submitquiz section

                # if this is the last quiz navigate to submitquiz view
                if submission.isLastUnAnsweredQuestion():

                    # calculate and store score value
                    attempt.calculate_and_set_score()
                    return HttpResponseRedirect(
                        reverse('quiz:submitQuiz',
                                kwargs={'pk':quiz.id,
                                        'user_attempt_no':attempt.user_attempt_no}))
                # otherwise navigate to the next question
                else:
                    next_question = submission.getNextQuestion()
                    print('\n\n\n\n\n\n', next_question, '\n\n\n\n')
                    return HttpResponseRedirect(
                        reverse('quiz:question',
                                kwargs={'question_id':next_question.id, 'pk':quiz.id,
                                        'user_attempt_no':attempt.user_attempt_no}))
            else:
                return HttpResponseRedirect(
                    reverse('quiz:submitQuiz',
                            kwargs={'pk':quiz.id,
                                'user_attempt_no':attempt.user_attempt_no}))
 
            # results = AnswersSubmitted.objects.filter(
            #     question__in=quiz_questions,
            #     attempt=attempt)
            # answered_questions = results.values('question')
            # unanswered_questions = quiz_questions.exclude(id__in=answered_questions)


            # if quiz_questions.filter(id=next_question_id):
            #     next_question=quiz_questions.get(id=next_question_id)
            #     return HttpResponseRedirect(
            #         reverse('quiz:question',
            #         kwargs={'question_id':next_question_id, 'pk':quiz.id,
            #                 'user_attempt_no':attempt.user_attempt_no}))

            # elif unanswered_questions.count() > 0:

            #     #find the earliest of the unanswered questions
            #     # redirect to it.
            #     first_question=unanswered_questions.order_by('id')[:1].get()

            #     return HttpResponseRedirect(
            #         reverse('quiz:question',
            #                 kwargs={'question_id':first_question.id,
            #                         'pk':quiz.id,
            #                     'user_attempt_no':attempt.user_attempt_no}))

            # else:
            #     answers = Answer.objects.filter(question__in=quiz_questions)
            #     results = AnswersSubmitted.objects.filter(
            #         question__in=quiz_questions,
            #         attempt=attempt)
            #     selected_answers = Answer.objects.filter(answerssubmitted__in=results)
            #     # determine the score the percentage of answers correct
            #     correct_answers=selected_answers.filter(correct_bool=True).count()
            #     all_answers=selected_answers.count()
            #     score=correct_answers / all_answers *100
            #     QuizAttempt.objects.filter(id=attempt.id).update(score=score)

            #     return HttpResponseRedirect(
            #         reverse('quiz:submitQuiz',
            #                 kwargs={'pk':quiz.id,
            #                     'user_attempt_no':attempt.user_attempt_no}))
        return HttpResponseRedirect('/quiz/')


class SubmitQuizView(LoginRequiredMixin, generic.TemplateView):
    login_url = '/account/login/'
    redirect_field_name = 'redirect_to'
    template_name='quiz/submitQuiz.html'

    def get(self, request, *args, **kwargs):
        #The goal is to display the results of that attempt of the quiz
        quiz_id = self.kwargs.pop('pk')
        user_attempt_no = self.kwargs.pop('user_attempt_no')
        quiz = Quiz.objects.get(id=quiz_id)
        attempt = QuizAttempt.objects.get(user=request.user,quiz=quiz,
                                          user_attempt_no=user_attempt_no)
        questions = Question.objects.filter(quiz=quiz)

        answers = Answer.objects.filter(question__in=questions)
        results = AnswersSubmitted.objects.filter(question__in=questions,
                                                  attempt=attempt)
        selected_answers = Answer.objects.filter(answerssubmitted__in=results)

        answered_questions = results.values('question')
        unanswered_questions = questions.exclude(
            id__in=answered_questions)
        answered_questions=questions.filter(id__in=answered_questions)

        answered_questions = answered_questions.annotate(
            answered_bool=Value(True, BooleanField()))
        unanswered_questions = unanswered_questions.annotate(
            answered_bool=Value(False, BooleanField()))
        status_questions = answered_questions.union(unanswered_questions).order_by('id')

        # report the score and the time_taken
        progress=attempt.progress(request.user, quiz)
        return render(request, self.template_name,
                      {'quiz':quiz,
                       'results':results, 'attempt':attempt,
                       'questions':status_questions, 'answers':answers,
                       'selected_answers':selected_answers,
                       'progress':progress, 'username':request.user
                       })

    def post(self, request, *args, **kwargs):
        quiz_id = self.kwargs.pop('pk')
        user_attempt_no = self.kwargs.pop('user_attempt_no')

        # determine the time taken
        attempt = QuizAttempt.objects.get(user=request.user,quiz=quiz_id,
                                          user_attempt_no=user_attempt_no)
        attempt.finish_time=timezone.now()
        attempt.submitted_bool=True
        attempt.save()

        attempt.time_taken=attempt.finish_time - attempt.start_time
        attempt.save()

        return HttpResponseRedirect(
            reverse('quiz:endQuiz', kwargs={'pk':quiz_id,
                                'user_attempt_no':attempt.user_attempt_no}))


class EndOfQuizView(LoginRequiredMixin, generic.TemplateView):
    login_url = '/account/login/'
    redirect_field_name = 'redirect_to'
    template_name='quiz/endQuiz.html'

    def get(self, request, *args, **kwargs):
        #The goal is to display the results of that attempt of the quiz
        quiz_id = self.kwargs.pop('pk')
        user_attempt_no = self.kwargs.pop('user_attempt_no')
        quiz = Quiz.objects.get(id=quiz_id)
        attempt = QuizAttempt.objects.get(user=request.user, quiz=quiz,
                                          user_attempt_no=user_attempt_no)
        questions = Question.objects.filter(quiz=quiz)

        answers = Answer.objects.filter(question__in=questions)
        results = AnswersSubmitted.objects.filter(question__in=questions,
                                                  attempt=attempt)
        selected_answers=Answer.objects.filter(answerssubmitted__in=results)
        # report the score and the time_taken
        score= attempt.score

        return render(request, self.template_name,
                      {'quiz':quiz, 'attempt':attempt,
                       'results':results, 'username':request.user,
                       'questions':questions, 'answers':answers,
                       'selected_answers':selected_answers,
                       'score':score})
