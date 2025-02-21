from django import forms
from .models import AuctionItem
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
class AuctionForm(forms.ModelForm):
    class Meta:
        model = AuctionItem
        fields = ['title', 'description', 'starting_bid', 'category', 'image', 'end_time']
        widgets = {
            'end_time': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                }
            )
        }


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
