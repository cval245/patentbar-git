from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.db import models
from django.db.models import Value, BooleanField, ForeignKey, IntegerField
from django.views import generic
from django.http import Http404, HttpResponseRedirect
from django.utils import timezone
from django.urls import reverse

from .models import Course, Module, Content
from quiz.models import Quiz
from userProfile.models import QuizAttempt, CourseCompletion,ModuleCompletion
# Create your views here.

class MainCourseView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'course/course_main.html'

    def get(self, request, *args, **kwargs):
        courses = Course.objects.all().order_by('order_no')
        modules = Module.objects.all()
        return render(request, self.template_name,
                      {'username':request.user, 'courses':courses,
                       'modules':modules})

    def post(self, request, *args, **kwargs):
        course_id=request.POST.get('course_id', '')
        course = Course.objects.get(id=course_id)
        course_attempt=CourseCompletion.objects.\
            get_or_create(user=request.user,
                          course=course)
        course_attempt = course_attempt[0]
        modules = Module.objects.filter(course=course)
        modules=modules.annotate(course_attempt=Value(course_attempt.id, ForeignKey(ModuleCompletion, on_delete=models.CASCADE)))
        mod_comp=modules.values('id', 'course_attempt')

        newModuleAttempts=[]
        modco=ModuleCompletion.objects.filter(course_attempt=course_attempt)
        if modules.count() > modco.count():
            for mod in mod_comp:
                mod['course_attempt']=CourseCompletion.objects.get(
                    id=mod['course_attempt'])
                newModuleAttempts.append(ModuleCompletion(
                    course_attempt=mod['course_attempt'],
                    module_id=mod['id']))
            ModuleCompletion.objects.bulk_create(newModuleAttempts)
        return HttpResponseRedirect(reverse('course:course',
                                        kwargs={'course_id':course.id}))

class CourseView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'course/course.html'
    def get(self, request, *args, **kwargs):
        course_id = self.kwargs.pop('course_id')
        course = Course.objects.get(id=course_id)
        modules = Module.objects.filter(course=course)

        return render(request, self.template_name,
                      {'username':request.user, 'course':course,
                       'modules':modules})

class ModuleView(LoginRequiredMixin, generic.TemplateView):
    template_beginning_of_course = 'course/module_beginning.html'
    template_next_module = 'course/module_next.html'
    template_end_of_course = 'course/module_end.html'

    def get(self, request, *args, **kwargs):
        course_id = self.kwargs.pop('course_id')
        module_id = self.kwargs.pop('module_id')
        course = Course.objects.get(id=course_id)
        module = Module.objects.get(id=module_id)
        contents = Content.objects.filter(module=module)

        #Calculate Next Module and previous module of course
        modules_all = Module.objects.filter(course=course).order_by('order_no')

        get_next_mod=False
        previous_mod = module.id
        for mod in modules_all:
            if mod.id == module.id:
                get_next_mod = True
                next_mod_id = mod.id
            elif get_next_mod == True:
                next_mod_id = mod.id
                break;
            # This is to identify previous modulea (it relies upon the break)
            if get_next_mod == False:
                previous_mod = mod.id
        
        previous_module = Module.objects.get(id=previous_mod)

        quiz=module.quiz

        #Calculates the status_module for modules that have already been read
        course_attempt=CourseCompletion.objects.get(user=request.user,
                                                       course=course)
        modules_attempts_answered=ModuleCompletion.objects.filter(course_attempt=course_attempt, finished_bool=True)
        completed_modules=Module.objects.filter(modulecompletion__in=modules_attempts_answered).filter(course=course)
        uncompleted_modules=Module.objects.exclude(modulecompletion__in=modules_attempts_answered).filter(course=course)
        completed_modules = completed_modules.annotate(
            completed_bool=Value(True, BooleanField()))
        uncompleted_modules = uncompleted_modules.annotate(
            completed_bool=Value(False, BooleanField()))
        status_modules =completed_modules.union(uncompleted_modules).order_by('order_no')

        # if this is the first module of the course (no previous module)
        if previous_module.id == module.id:
            next_module = Module.objects.get(id=next_mod_id)
            return render(request, self.template_beginning_of_course,
                          {'username':request.user, 'course':course,
                           'module':module, 'contents':contents,
                           'status_modules':status_modules,
                           'modules_all':modules_all,
                           'next_module':next_module,
                           'quiz': quiz})

        # if there is NOT a next_module (last module in course)
        elif next_mod_id == module.id:
            return render(request, self.template_end_of_course,
                          {'username':request.user, 'course':course,
                           'module':module, 'contents':contents,
                           'status_modules':status_modules,
                           'modules_all':modules_all,
                           'previous_module':previous_module,
                           'quiz':quiz})
        # if there is a next_module
        else:
            next_module = Module.objects.get(id=next_mod_id)
            return render(request, self.template_next_module,
                      {'username':request.user, 'course':course,
                       'module':module,'next_module':next_module,
                       'contents':contents, 'modules_all':modules_all,
                       'status_modules':status_modules,
                       'previous_module':previous_module,
                       'quiz':quiz
                      })

        raise Http404

    def post(self, request, *args, **kwargs):
        course_id = self.kwargs.pop('course_id')
        module_id = self.kwargs.pop('module_id')
        course = Course.objects.get(id=course_id)
        module = Module.objects.get(id=module_id)
        contents = Content.objects.filter(module=module)

        #Calculate Next Module and previous module of course
        modules_all = Module.objects.filter(course=course).order_by('order_no')
        get_next_mod=False
        previous_mod = module.id
        for mod in modules_all:
            if mod.id == module.id:
                get_next_mod = True
                next_mod_id = mod.id
            elif get_next_mod == True:
                next_mod_id = mod.id
                break;
            # This is to identify previous modulea (it relies upon the break)
            if get_next_mod == False:
                previous_mod = mod.id
        
        previous_module = Module.objects.get(id=previous_mod)

        quiz=module.quiz

        # update position in course
        course_attempt=CourseCompletion.objects.get(user=request.user,
                                                    course=course)
        module_attempt=ModuleCompletion.objects.get(
            course_attempt=course_attempt, module=module)
        module_attempt.set_module_complete()

        if course_attempt.finished_bool==False:
            # find all modules in course
            modules = Module.objects.filter(course=course)
            # find the completed modules
            completed_modules=ModuleCompletion.objects.filter(
                course_attempt=course_attempt,
                finished_bool=True)
            course_attempt.set_course_completed()
        if module.quiz:
            return HttpResponseRedirect(reverse('quiz:detail',
                                            kwargs={'pk':module.quiz.id}))

        # if there is no next module
        elif next_mod_id == module.id:
            return HttpResponseRedirect(reverse('course:course',
                                  kwargs={'course_id':course.id}))
        # if there is a next_module
        else:
            next_module = Module.objects.get(id=next_mod_id)
            return HttpResponseRedirect(reverse('course:module',
                                        kwargs={'course_id':course.id,
                                                'module_id':next_module.id}))
