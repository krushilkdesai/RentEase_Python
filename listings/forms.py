from django import forms
from .models import House, UserProfile, ContactMessage, HouseImage
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Comment, Review

class HouseForm(forms.ModelForm):
    class Meta:
        model = House
        fields = ['name', 'price', 'image', 'bedrooms', 'beds', 'bathrooms', 'location', 'description', 'contact_name', 'contact_mobile', 'contact_email']

class RegisterForm(UserCreationForm):
    username = forms.CharField(label='Username', help_text=None)
    email = forms.EmailField(required=True)
    profile_image = forms.ImageField(required=False)
    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "profile_image", "first_name", "last_name", "bio"]

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_image', 'first_name', 'last_name', 'bio']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Full Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Phone Number (Optional)'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject of your message'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Write your message here...'
            }),
        }