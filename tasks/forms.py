from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Event, Category


# Event Form
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'date', 'time', 'location', 'category']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'bg-gray-700 text-white p-2 rounded w-full'
            }),
            'description': forms.Textarea(attrs={
                'class': 'bg-gray-700 text-white p-2 rounded w-full'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'bg-gray-700 text-white p-2 rounded w-full'
            }),
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'bg-gray-700 text-white p-2 rounded w-full'
            }),
            'location': forms.TextInput(attrs={
                'class': 'bg-gray-700 text-white p-2 rounded w-full'
            }),
            'category': forms.Select(attrs={
                'class': 'bg-gray-700 text-white p-2 rounded w-full'
            }),
        }

    def clean_date(self):
        date = self.cleaned_data['date']
        if date < timezone.now().date():
            raise ValidationError("Event date cannot be in the past.")
        return date


# User Registration Form (replaces old ParticipantForm)
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full p-2 border border-gray-300 rounded',
            'placeholder': 'Enter your email'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded',
                'placeholder': 'Choose a username'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email


# Category Form
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Category.objects.filter(name__iexact=name).exists():
            raise ValidationError("A category with this name already exists.")
        return name
