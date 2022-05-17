from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.db.models import F
import urllib3

from .models import User, Listings, Bids, Comments, Watchlist, FinishedListings
from .forms import ListingsForm, BidsForm, FinishedListingsForms, CommentsForm


def check_bid(listing_id, bid):
    '''
    Checking if bid is correctly placed
    '''
    # Find listing and assign it into instance
    try:
        listing = Listings.objects.get(pk=listing_id)
    except Listings.DoesNotExist:
        return False
    
    # Create current instance, order by bid, descending
    bid_instance = listing.bidded.order_by('-bid').first()

    # Return False if auction was set up incorrectly
    if not bid_instance:
        return False
    # Assign current bid
    else:
        bid_current = bid_instance.bid

    if bid > bid_current:
        return True
    else:
        return False


def current_price(listing_id):
    '''
    Returning the current price of an item
    '''
    # Find listing and assign it into instance
    try:
        listing = Listings.objects.get(pk=listing_id)
    except Listings.DoesNotExist:
        return None
    
    # Order the bids decending and fetch the first one
    bid_instance = listing.bidded.order_by('-bid').first()

    # In case error
    if not bid_instance:
        return None
    return bid_instance.bid
    

def current_leader(listing_id):
    '''
    Returns owner of the highest bid as an user instance
    '''
    # Find listing and assign it into instance
    try:
        listing = Listings.objects.get(pk=listing_id)
    except Listings.DoesNotExist:
        return None
  
    # Order the bids decending and fetch the first one
    bid_instance = listing.bidded.order_by('-bid').first()

    # In case auction was created incorrectly
    if not bid_instance:
        return None
    return bid_instance.bidder


def index(request):
    try:
        listings = Listings.objects.all()
        
    except Listings.DoesNotExist:
        return render(request, "auctions/index.html", {
        "listings": None
    })

    data = []
    # Assign data to list and add current price
    for listing in listings:
        if not listing.finished.first():
            data.append({
                'data': listing,
                'price': current_price(listing.id)
        })

    return render(request, "auctions/index.html", {
        "listings": data
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create(request):
    if request.method == "POST":
        # Collect data from form
        form = ListingsForm(request.POST)

        # Validate data
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            category = form.cleaned_data["category"]
            bid_start = form.cleaned_data["bid_start"]
            image = form.cleaned_data["image"]

            # Default image
            default_image = "https://img.ifunny.co/images/747a223f705610d1e7a42c4a1a688dea5c5d180d317271f66b4b24e48bf84d26_1.webp" 

            # Check if link was provided and is valid. If not append deafault picture.
            if image:
                try:
                    http = urllib3.PoolManager()
                    resp = http.request("GET", image)
                except:
                    image = default_image  
            else:
                image = default_image

            # Get user id and make it an "User instance". It is necessary when dealing with User table.
            user_id = request.user.id
            author = User.objects.get(id=user_id)

            # Add listing to database
            listing = Listings.objects.create(
                title=title,
                description=description,
                category=category,
                image=image,
                bid_start=bid_start,
                author=author
                )
            # Firts bid is listing author starting price
            bids = Bids.objects.create(
                listing=listing,
                bidder=author,
                bid=bid_start
            )
            return HttpResponseRedirect(reverse('index'))
        else:
            # Return form with wrong data, if it was not valid
            return render(request, "auctions/create.html", {
            "form": form
            }) 

    # Render the page
    else:         
        return render(request, "auctions/create.html", {
            "form": ListingsForm()
        })


def listing(request, listing_id):
    # Check if listing exists, if so load it into variables
    try:
        listing = Listings.objects.get(pk=listing_id)
    except Listings.DoesNotExist:
        raise Http404("Listing not found.")
    
    # Assign current price
    price = current_price(listing_id)
    leader = current_leader(listing_id)


    # Check is on finished auctions list
    try:
        finished_list = FinishedListings.objects.get(title=listing)
    except FinishedListings.DoesNotExist:
        finished_list = None

    # Load comments if they exist
    comments = Comments.objects.filter(listing=listing).all()
    if not comments:
        comments = None

    # If user is logged
    user_id = request.user.id
    if user_id:
        user = User.objects.get(pk=user_id)

        # Check if listed item is on users watchlist
        try:
            watchlist = Watchlist.objects.get(user=user, listing=listing_id)
        except Watchlist.DoesNotExist:
            watchlist = None

        # Populate bid form with users data
        bid_data = {'bidder': user_id, 'listing': listing_id}
        form_bid = BidsForm(bid_data)

        # Check if user is the author of the listing
        if user == listing.author:
            # Populate finish form
            finish_data = {'title': listing.id}
            form_finish = FinishedListingsForms(finish_data)
        else:
            form_finish = None

        # Prepopulate comments form    
        comment_data = {'author': user_id, 'listing': listing_id }
        form_comment = CommentsForm(comment_data)
    # If user is not logged in
    else:
        watchlist = None
        form_bid = None
        form_finish = None
        form_comment = None

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "watchlist": watchlist,
        "price": price,
        "form_bid": form_bid,
        "form_finish": form_finish,
        "leader": leader,
        "finished": finished_list,
        "form_comment": form_comment,
        "comments": comments
    })


@login_required
def watchlist(request):
    user_id = request.user.id
    user = User.objects.get(pk=user_id)

    # If we adding/deleting from watchlist
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        action = request.POST["action"]
        sender = request.POST["sender"]

        listing = Listings.objects.get(pk=listing_id)
        
        watchlist_user = Watchlist.objects.filter(user=user).first()
        if action == "add":
            if not watchlist_user:
                entry = Watchlist.objects.create(user=user)
                entry.listing.add(listing)
            else:
                watchlist_user.listing.add(listing)
        else:
            watchlist_user.listing.remove(listing)

        if sender == "listing":
            return HttpResponseRedirect(reverse('listing', args=(listing_id,)))
        else:
            return HttpResponseRedirect(reverse('watchlist'))
    
    # If we rendering the watchlist
    else:

        # Get users watchlist
        try:
            query = Watchlist.objects.get(user=user)
        except Watchlist.DoesNotExist:
            return render(request, 'auctions/watchlist.html')

        # Get all the elements on the users watchlist and render the view
        watchlist = query.listing.all()
        return render(request, 'auctions/watchlist.html', {
            "watchlist": watchlist
        })


@login_required
def bid(request):
    form = BidsForm(request.POST)

    # Validate form
    if form.is_valid():
        bid = form.cleaned_data["bid"]
        bidder = form.cleaned_data["bidder"]
        listing = form.cleaned_data["listing"]
        listing_id = listing.id
        
        # Check if bid is correct
        if not check_bid(listing.id, bid):
            return render(request, 'auctions/status.html', {
                "message": "Your bid should be bigger than the current bid.",
                "listing_id": listing_id
                })
                    
        # Record the bid
        record_bid = Bids.objects.create(
            listing=listing,
            bidder=bidder,
            bid=bid
        )
        return render(request, 'auctions/status.html', {
                "message": "You have successfully placed the bid!",
                "listing_id": listing_id
                })
    else:
        return render(request, 'auctions/status.html', {
                "message": "Your bid was somewhat incorrect, sorry"
                })
    

def finish(request):
    if request.method == "POST":
        form = FinishedListingsForms(request.POST)

        # Validate form
        if form.is_valid():
            listing = form.cleaned_data["title"]
            bid_instance = listing.bidded.order_by('-bid').first()

            finish_lisitng = FinishedListings.objects.create(
                title=listing,
                winner=bid_instance.bidder,
                bid_end=bid_instance
            )

            # Check if there were no other bids than starting bid by author of the listing
            if listing.author == bid_instance.bidder:
                return render(request, 'auctions/status.html', {
                    "message": "You have successfully closed the auction without any bids on it."
                    })

            return render(request, 'auctions/status.html', {
                    "message": "You have successfully closed the auction."
                    }) 
        else:
            return render(request, 'auctions/status.html', {
                    "message": "Something went wrong, try again later."
                    })
    else:
        try:
            finished = FinishedListings.objects.all()
        except FinishedListings.DoesNotExist:
            return render(request, 'auctions/finished.html')

        return render(request, 'auctions/finished.html', {
            'finished_list': finished
        })


def comment(request):
    form = CommentsForm(request.POST)

    # Validate form
    if form.is_valid():
        listing = form.cleaned_data["listing"]
        author = form.cleaned_data["author"]
        comment = form.cleaned_data["comment"]

        listing_id = listing.id

        # Create comment
        create_comment = Comments.objects.create(
            comment=comment,
            author=author,
            listing=listing
        )
        return HttpResponseRedirect(reverse('listing', args=(listing_id,)))
    else:
        return render(request, 'auctions/status.html', {
                    "message": "Your comment was somewhat invalid."
                    }) 


def categories(request):
    # Query for categories
    categories = Listings.objects.values('category').distinct()
        
    return render(request, 'auctions/categories.html', {
        'categories': categories
    })


def category(request, category_name):
    category_items = Listings.objects.filter(category=category_name).all()
    data = []

    # Append item if it is not on finished list
    for item in category_items:
        if not item.finished.first():
            data.append(item)

    return render(request, 'auctions/category.html', {
        "category": data,
        "name": category_name
        })