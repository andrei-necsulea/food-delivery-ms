from django.urls import path

from . import views

urlpatterns = [
    path('<int:pk>/', views.payment_detail, name='payment_detail'),
    path('<int:pk>/confirm/', views.payment_confirm, name='payment_confirm'),
    path('<int:pk>/fail/', views.payment_fail, name='payment_fail'),
]
