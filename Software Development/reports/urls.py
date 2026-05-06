from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('driver-performance/', views.driver_performance_report, name='driver_performance'),
    path('driver-performance/export/', views.export_driver_performance, name='export_driver_performance'),
    path('export/', views.export_report, name='export_report'),
    path('restaurant-sales/', views.restaurant_sales_report, name='restaurant_sales'),
    path('revenue/', views.revenue_analytics, name='revenue_analytics'),
    path('orders/', views.order_analytics, name='order_analytics'),
    path('deliveries/', views.delivery_analytics, name='delivery_analytics'),
    path('system-logs/', views.system_logs, name='system_logs'),
]
