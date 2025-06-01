from django.contrib import admin
from .models import AuctionItem, Bid

admin.site.register(AuctionItem)
admin.site.register(Bid)