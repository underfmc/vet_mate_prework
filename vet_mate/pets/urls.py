from django.urls import path

from . import views


app_name = 'pets'

urlpatterns = [
    path('', views.PetListView.as_view(), name="pets_list"),
    path('add/', views.PetCreateView.as_view(), name="add_pet"),
    path('ajax/load-breeds/', views.load_breeds, name='load_breeds'),
    path('<slug:slug>/', views.pet_detail, name="pet_detail"),
    path('<slug:slug>/edit', views.PetUpdateView.as_view(), name="pet_edit"),
    path('<slug:slug>/delete', views.PetDeleteView.as_view(),
         name="pet_delete"),
]
