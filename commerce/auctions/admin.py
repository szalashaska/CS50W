from django.contrib import admin

from .models import Listings, Bids, Comments, Watchlist, FinishedListings, User

# Register your models here.

class WatchlistAdmin(admin.ModelAdmin):
    filter_horizontal = ("listing",)

admin.site.register(User)
admin.site.register(Listings)
admin.site.register(Bids)
admin.site.register(Comments)
admin.site.register(Watchlist, WatchlistAdmin)
admin.site.register(FinishedListings)