from django.urls import path
from . import views

urlpatterns = [
    path('', views.delivery_list, name='delivery_list'),
    path('create/', views.delivery_create, name='delivery_create'),
    path('update/<int:pk>/', views.delivery_update, name='delivery_update'),
    path('delete/<int:pk>/', views.delivery_delete, name='delivery_delete'),
]