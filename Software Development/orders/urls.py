from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('update/<int:pk>/', views.order_update, name='order_update'),
    path('cancel/<int:pk>/', views.order_cancel, name='order_cancel'),
    path('delete/<int:pk>/', views.order_delete, name='order_delete'),

    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:menu_item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),
]