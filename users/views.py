from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic.edit import FormView
from users.forms import CustomUserCreationForm
# Create your views here.

class DashboardView(LoginRequiredMixin, View):
    login_url = 'login/'
    redirect_field_name = 'next'
    template_name = 'registration/dashboard.html'

    def get(self, request, *args, **kwargs):
        username = request.user
        return render(request, self.template_name, {'username': username})


class SignUpView(FormView):
    template_name = 'registration/signup.html'
    form_class = CustomUserCreationForm
    success_url = '/account/'

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url())
