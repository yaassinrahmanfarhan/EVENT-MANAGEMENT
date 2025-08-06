from django import forms
from .models import Event, Participant, Category
from django.core.exceptions import ValidationError
from django.utils import timezone


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'date', 'time', 'location', 'category']

        widgets = {
    'name': forms.TextInput(attrs={'class': 'bg-gray-700 text-white p-2 rounded w-full'}),
    'description': forms.Textarea(attrs={'class': 'bg-gray-700 text-white p-2 rounded w-full'}),
    'date': forms.DateInput(attrs={'type': 'date', 'class': 'bg-gray-700 text-white p-2 rounded w-full'}),
    'time': forms.TimeInput(attrs={'type': 'time', 'class': 'bg-gray-700 text-white p-2 rounded w-full'}),
    'location': forms.TextInput(attrs={'class': 'bg-gray-700 text-white p-2 rounded w-full'}),
    'category': forms.Select(attrs={'class': 'bg-gray-700 text-white p-2 rounded w-full'}),
}


    def clean_date(self):
        date = self.cleaned_data['date']
        if date < timezone.now().date():
            raise ValidationError("Event date cannot be in the past.")
        return date




class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['name', 'email', 'events']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded',
                'placeholder': 'Enter participant name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded',
                'placeholder': 'Enter participant email'
            }),
            'events': forms.CheckboxSelectMultiple(attrs={
                'class': 'space-y-2'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email or "@" not in email:
            raise ValidationError("Please enter a valid email address.")
        return email


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Category.objects.filter(name__iexact=name).exists():
            raise ValidationError("A category with this name already exists.")
        return name
