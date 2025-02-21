from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
class AuctionItem(models.Model):
    CATEGORY_CHOICES = [
        ('Electronics', 'Electronics'),
        ('Fashion', 'Fashion'),
        ('Home Goods', 'Home Goods'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='auction_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
   # New fields for auction end time and winner
    end_time = models.DateTimeField(null=True, blank=True)
    winner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="won_auctions"
    )

    def __str__(self):
        return self.title

    @property
    def is_closed(self):
        """Return True if the auction has ended."""
        return self.end_time and timezone.now() >= self.end_time

class Bid(models.Model):
    auction = models.ForeignKey(AuctionItem, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bidder.username} bid ${self.amount} on {self.auction.title}"