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

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        if self.cleaned_data.get('role') == 'admin':
            user.is_superuser = True
        else:
            user.is_superuser = False

        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile information"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'vehicle_type', 'vehicle_plate', 'date_of_birth', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'vehicle_type': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_plate': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }