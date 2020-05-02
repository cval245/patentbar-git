from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import generic
from django.http import Http404

from .models import Course, Module, Content
# Create your views here.

class MainCourseView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'course/course_main.html'

    def get(self, request, *args, **kwargs):
        courses = Course.objects.all()
        modules = Module.objects.all()
        return render(request, self.template_name,
                      {'username':request.user, 'courses':courses,
                       'modules':modules})


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

        # if this is the first module of the course (no previous module)
        if previous_module.id == module.id:
            next_module = Module.objects.get(id=next_mod_id)
            return render(request, self.template_beginning_of_course,
                          {'username':request.user, 'course':course,
                           'module':module, 'contents':contents,
                           'modules_all':modules_all,
                           'next_module':next_module})
        

        # if there is NOT a next_module (last module in course)
        elif next_mod_id == module.id:
            return render(request, self.template_end_of_course,
                          {'username':request.user, 'course':course,
                           'module':module, 'contents':contents,
                           'modules_all':modules_all,
                           'previous_module':previous_module})
        # if there is a next_module
        else:
            next_module = Module.objects.get(id=next_mod_id)
            return render(request, self.template_next_module,
                      {'username':request.user, 'course':course,
                       'module':module,'next_module':next_module,
                       'contents':contents, 'modules_all':modules_all,
                       'previous_module':previous_module
                      })

        raise Http404
