from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import ClientDriverRegistrationForm, AdminManagerCreationForm, UserProfileForm
from .decorators import role_required


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get_success_url(self):
        user = self.request.user

        if user.role == 'admin':
            return reverse_lazy('home')
        elif user.role == 'manager':
            return reverse_lazy('home')
        elif user.role == 'client':
            return reverse_lazy('home')
        elif user.role == 'driver':
            return reverse_lazy('home')

        return reverse_lazy('home')


def register_view(request):
    """Public registration for Client and Delivery Driver"""
    if request.method == 'POST':
        form = ClientDriverRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created.')
            return redirect('home')
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = ClientDriverRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form, 'title': 'Register'})


@role_required(allowed_roles=['admin', 'manager'])
def create_admin_user_view(request):
    """Protected view for Admin and Manager to create Admin/Manager accounts"""
    if request.method == 'POST':
        form = AdminManagerCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'{user.get_role_display()} account "{user.username}" has been created.')
            return redirect('admin:auth_user_changelist')  # Redirect to Django admin
        else:
            messages.error(request, 'Account creation failed. Please correct the errors below.')
    else:
        form = AdminManagerCreationForm()

    return render(request, 'accounts/create_admin_user.html', {'form': form})


def profile_view(request):
    """View user profile"""
    user = request.user
    return render(request, 'accounts/profile.html', {'user': user})


def update_profile_view(request):
    """Update user profile"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'accounts/update_profile.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')