from django import forms
from django.forms import ModelForm, Textarea
from django.utils.translation import gettext_lazy as _
from .models import Bids, FinishedListings, Comments

# Form created in classical way
class ListingsForm(forms.Form):
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

    title = forms.CharField(label="Title", max_length=64)
    description = forms.CharField(label="Description", max_length=256, widget=forms.Textarea())
    # Make image field 'category' and 'image' optional 
    category = forms.CharField(max_length=20, widget=forms.Select(choices=CATEGORY_CHOICES), initial="None")
    image = forms.URLField(max_length=128, required=False)
    bid_start = forms.FloatField()


# Form created using ModelForm method
class BidsForm(ModelForm):
    class Meta:
        model = Bids
        fields = ['listing', 'bidder', 'bid']


class FinishedListingsForms(ModelForm):
    class Meta:
        model = FinishedListings
        fields = ['title']


class CommentsForm(ModelForm):
    class Meta:
        model = Comments
        fields = ['comment', 'author', 'listing']
        widgets = {
            'comment': Textarea(attrs={'cols': 50, 'rows': 5}),
        }