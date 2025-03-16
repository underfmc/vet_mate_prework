from django.urls import path

from . import views


app_name = 'vets'

urlpatterns = [
    path('', views.vets_list, name='vets_list'),
    path('clinic/<int:pk>/', views.clinic_detail, name='clinic_detail'),
    path('<int:pk>/', views.vet_detail, name='vet_detail'),
    path('vet_visits/', views.vet_visits, name='vet_visits'),
]
