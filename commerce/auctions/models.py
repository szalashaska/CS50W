from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Listings(models.Model):
    CATEGORY_CHOICES = [
        ('Cars', 'Cars'),
        ('Fashion','Fashion'),
        ('Electronics','Electronics'),
        ('Sport','Sport'),
        ('Toys','Toys'),
        ('Music','Music'),
        ('Home', 'Home'),
        ('Culture', 'Culture'),
        ('None', ''),
    ]

    title = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='None')
    image = models.URLField(max_length=256, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller")
    bid_start = models.FloatField()
    timestamp = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.title} sold by {self.author} in category {self.category}"
    

class Bids(models.Model):
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="bidded")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    bid = models.FloatField()
    
    def __str__(self):
        return f"Bidder {self.bidder} is bidding {self.listing} with amount {self.bid} \$"


class Comments(models.Model):
    comment = models.CharField(max_length=512)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commentators")
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="commented")

    def __str__(self):
        return f"User {self.author} commenting on {self.listing}"


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watcher")
    listing = models.ManyToManyField(Listings, related_name="watched")

    def __str__(self):
        return f"User {self.user}'s watched items"


class FinishedListings(models.Model):
    title = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="finished")
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="winner")
    bid_end = models.ForeignKey(Bids, on_delete=models.CASCADE, related_name="bid_end")

    def __str__(self):
        return f"User {self.winner} won the auction: {self.title}"