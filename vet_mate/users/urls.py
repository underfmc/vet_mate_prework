from django.urls import path

from . import views


app_name = 'users'


urlpatterns = [
    path('registration/', views.UserCreateView.as_view(), name='registration'),
    path('subscriptions/', views.SubscriptionListView.as_view(),
         name='subscriptions'),
    path('create_subscription/<int:pk>/', views.create_subscription,
         name='create_subscription'),
    path('<slug:slug>/edit/', views.UserUpdateView.as_view(), name='edit'),
    path('<slug:slug>/', views.UserDetailView.as_view(), name='profile'),
]
