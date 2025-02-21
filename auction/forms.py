from django import forms
from .models import AuctionItem

class AuctionForm(forms.ModelForm):
    class Meta:
        model = AuctionItem
        fields = ['title', 'description', 'starting_bid', 'category', 'image']
