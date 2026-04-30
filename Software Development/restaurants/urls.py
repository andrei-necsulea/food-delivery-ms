from django.urls import path
from . import views

urlpatterns = [
    path('', views.restaurant_list, name='restaurant_list'),
    path('create/', views.restaurant_create, name='restaurant_create'),
    path('update/<int:pk>/', views.restaurant_update, name='restaurant_update'),
    path('delete/<int:pk>/', views.restaurant_delete, name='restaurant_delete'),
    path('<int:pk>/', views.restaurant_detail, name='restaurant_detail'),
]