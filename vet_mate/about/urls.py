from django.urls import path

from . import views


appname = 'about'

urlpatterns = [
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('terms/', views.TermsView.as_view(), name='terms'),
]
