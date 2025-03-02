from django.urls import path

from . import views


app_name = 'vets'

urlpatterns = [
    path('', views.vets_list, name='vets_list'),
    path('<int:id>/', views.vet_detail, name='vet_detail')
]
