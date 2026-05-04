from django.urls import path
from .views import CustomLoginView, register_view, logout_view, create_admin_user_view, profile_view, update_profile_view

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('admin/create-user/', create_admin_user_view, name='create_admin_user'),
    path('profile/', profile_view, name='profile'),
    path('profile/update/', update_profile_view, name='update_profile'),
]