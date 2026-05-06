from django.urls import path
from . import views

urlpatterns = [
    path('', views.delivery_list, name='delivery_list'),
    path('available/', views.available_orders, name='available_orders'),
    path('take/<int:order_id>/', views.take_order, name='take_order'),
    path('create/', views.delivery_create, name='delivery_create'),
    path('update/<int:pk>/', views.delivery_update, name='delivery_update'),
    path('delete/<int:pk>/', views.delivery_delete, name='delivery_delete'),
    path('reassign-courier/<int:pk>/', views.delivery_reassign_courier, name='delivery_reassign_courier'),
    path('courier/<int:pk>/', views.courier_info, name='courier_info'),
]