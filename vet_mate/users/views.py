from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .forms import CreationForm
from .models import Subscription
from django.utils import timezone

User = get_user_model()


class SubscriptionListView(LoginRequiredMixin, ListView):
    model = Subscription
    template_name = 'users/subscriptions.html'
    context_object_name = 'object_list'
    ordering = 'name'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['current_subscription'] = user.subscription
        if user.subscription and user.subscription_start_date:
            # Рассчитываем дату окончания подписки
            context['subscription_end_date'] = (
                user.subscription_start_date +
                timezone.timedelta(days=user.subscription.duration))
        return context


def create_subscription(request, pk):
    user = request.user
    user.subscription = Subscription.objects.get(pk=pk)
    expired = (user.subscription_start_date +
               timezone.timedelta(days=user.subscription.duration) <
               timezone.now().date())
    if user.subscription is None or expired:
        user.subscription_start_date = timezone.now().date()
        user.save()
        return redirect('users:profile', slug=user.username)
    messages.error(request, 'Подписка уже активна')
    return redirect('users:subscriptions')


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
