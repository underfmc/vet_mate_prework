from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from .forms import CreationForm


User = get_user_model()


class UserCreateView(CreateView):
    template_name = 'users/registration_form.html'
    form_class = CreationForm
    success_url = reverse_lazy('homepage:index')


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = 'username'
    template_name = 'users/profile.html'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        try:
            obj = queryset.get(username=self.kwargs['slug'],
                               phone_number=self.request.user.phone_number)
        except User.DoesNotExist:
            raise Http404()

        return obj


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CreationForm
    slug_field = 'username'
    template_name = 'users/registration_form.html'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        try:
            obj = queryset.get(username=self.kwargs['slug'],
                               phone_number=self.request.user.phone_number)
        except User.DoesNotExist:
            raise Http404()

        return obj
