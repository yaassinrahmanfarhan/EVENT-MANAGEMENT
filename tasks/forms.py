from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from .models import Event, Category
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.password_validation import password_validators_help_texts


# Event Form
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'name',
            'description',
            'date',
            'time',
            'location',
            'category',
            'image',  # Added image upload
        ]

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
            'image': forms.ClearableFileInput(attrs={
                'class': 'bg-gray-700 text-white p-2 rounded w-full'
            }),
        }

    def clean_date(self):
        date = self.cleaned_data['date']
        if date < timezone.now().date():
            raise ValidationError("Event date cannot be in the past.")
        return date


# User Registration Form (for signup with extra fields)
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full p-2 border border-gray-300 rounded',
            'placeholder': 'Enter your email'
        })
    )
    first_name = forms.CharField(
        required=True, 
        widget=forms.TextInput(attrs={
            'class': 'w-full p-2 border border-gray-300 rounded',
            'placeholder': 'First name'
        })
    )
    last_name = forms.CharField(
        required=True, 
        widget=forms.TextInput(attrs={
            'class': 'w-full p-2 border border-gray-300 rounded',
            'placeholder': 'Last name'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

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

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'text-black border border-gray-300 rounded w-full p-2 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'text-black border border-gray-300 rounded w-full p-2 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter password',
        })
    )

class StyledFormMixin:
    """
    Mixin to automatically apply Tailwind CSS styling and placeholders 
    to Django form fields for a consistent and user-friendly UI.
    """

    # Default classes for most input fields
    default_classes = (
        "border-2 border-gray-300 w-full p-3 rounded-lg shadow-sm "
        "focus:outline-none focus:border-rose-500 focus:ring-rose-500"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styled_widgets()

    def apply_styled_widgets(self):
        for field_name, field in self.fields.items():
            widget = field.widget

            # Determine placeholder text if not explicitly set
            placeholder = widget.attrs.get('placeholder', f"Enter {field.label.lower()}")

            # Apply styling based on widget type
            if isinstance(widget, (forms.TextInput, forms.EmailInput, forms.PasswordInput)):
                widget.attrs.update({
                    'class': self.default_classes,
                    'placeholder': placeholder
                })
            elif isinstance(widget, forms.Textarea):
                widget.attrs.update({
                    'class': f"{self.default_classes} resize-none",
                    'placeholder': placeholder,
                    'rows': 5
                })
            elif isinstance(widget, forms.SelectDateWidget):
                widget.attrs.update({
                    'class': self.default_classes
                })
            elif isinstance(widget, forms.CheckboxSelectMultiple):
                widget.attrs.update({
                    'class': "space-y-2"
                })
            else:
                # Fallback for other widgets
                widget.attrs.update({
                    'class': self.default_classes,
                    'placeholder': placeholder
                })

class CustomPasswordChangeForm(StyledFormMixin,PasswordChangeForm):
    pass

class CustomPasswordResetForm(StyledFormMixin, PasswordResetForm):
    pass

class CustomPasswordResetConfirmForm(StyledFormMixin, SetPasswordForm):
    pass


class EditProfileForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

    bio = forms.CharField(required=False, widget=forms.Textarea, label='Bio')
    profile_image = forms.ImageField(required=False, label='Profile Image')

    def __init__(self, *args, **kwargs):
        self.userprofile = kwargs.pop('userprofile', None)
        super().__init__(*args, **kwargs)
        print("forms", self.userprofile)

        # Todo: Handle Error

        if self.userprofile:
            self.fields['bio'].initial = self.userprofile.bio
            self.fields['profile_image'].initial = self.userprofile.profile_image

    def save(self, commit=True):
        user = super().save(commit=False)

        # Save userProfile jodi thake
        if self.userprofile:
            self.userprofile.bio = self.cleaned_data.get('bio')
            self.userprofile.profile_image = self.cleaned_data.get(
                'profile_image')

            if commit:
                self.userprofile.save()

        if commit:
            user.save()

        return user