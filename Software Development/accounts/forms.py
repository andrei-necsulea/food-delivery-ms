from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class ClientDriverRegistrationForm(UserCreationForm):
    """Public registration form - only for Client and Driver roles"""
    role = forms.ChoiceField(
        choices=[('client', 'Client'), ('driver', 'Delivery Driver')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='I want to register as:'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


class AdminManagerCreationForm(UserCreationForm):
    """Protected form - only for Admin and Manager roles (used by admins)"""
    role = forms.ChoiceField(
        choices=[('admin', 'Admin'), ('manager', 'Restaurant Manager')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='User Role:'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )