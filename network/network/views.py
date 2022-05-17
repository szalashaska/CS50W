import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .models import User, Posts, Follows, Likes

# Posts per page
POSTS_PER_PAGE = 10

def index(request):
    return render(request, "network/index.html")


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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

# API functions
@login_required
def create_post(request):
    # Only POST method accepted
    if request.method != "POST":
        return JsonResponse({"error": "POST method required."}, status=400)

    # Content of the users post should not be empty
    data = json.loads(request.body)
    content = data["body"]
    if content.strip() == "":
        return JsonResponse({"error": "Content of the post should not be empty."}, status=400)
    
    # Get user
    try:
        author = User.objects.get(pk=request.user.id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)
    
    # Create new post
    new_post = Posts.objects.create(
        author=author,
        content=content
    )
    return JsonResponse({"message": "Successfully added new post."}, status=201)


def posts(request, view):
    # Get number of page, that is requested
    page_number = request.GET['page']

    # Filter posts depending on the view, reverse chronological
    # All post
    if view == "all":
        data = Posts.objects.all().order_by("-timestamp")

    # Viewed user
    elif view == "userview":
        # Get viewed user from body of fetched data 
        person = request.GET['person']
        try:
            author = User.objects.get(username=person)
        except User.DoesNotExist:
            return JsonResponse({"error": "User does not exists."}, status=400)

        # Filter data
        data = Posts.objects.filter(author=author).all().order_by("-timestamp")
    
    # Filter post depending on users that are followed
    elif view == "following":
        # Get followed authors
        try:
            follower = Follows.objects.get(user=request.user)
        except Follows.DoesNotExist:
            return JsonResponse({"no_followed_users": True}, status=201)

        authors = []
        for author in follower.follows.all():
            authors.append(author)

        # Filter data
        data = Posts.objects.filter(author__in=authors).order_by("-timestamp")  
    else:
        return JsonResponse({"error": "Wrong view."}, status=400)

    # Check if there are any posts, return message if not
    if not data:
        return JsonResponse({"no_post_to_show": True}, status=201)

    # Prepere pagination data - use paginator object
    paginator = Paginator(data, POSTS_PER_PAGE)
    posts = paginator.get_page(page_number)

    # Prepere pagination data -> trying to use only Java Script on frontend
    pages = {}
    pages["number_of_pages"] = posts.paginator.num_pages

    if posts.has_previous():
        pages["has_previous"] = True
        pages["previous"] = posts.previous_page_number()

    if posts.has_next():
        pages["has_next"] = True
        pages["next"] = posts.next_page_number()
        pages["last"] = posts.paginator.num_pages

    # Show which posts are already liked by user, if logged in
    if request.user.id:
        user = User.objects.get(pk=request.user.id)
        
        # Check if post is on the liked list of user, append boolean
        serialized = []
        # For loop with index
        for index, post in enumerate(posts):
            if Likes.objects.filter(posts=post, user=user).first():
                serialized.append(post.serialize())
                # Add liked key-value to serialized data
                serialized[index]["liked"] = True

            else:
                serialized.append(post.serialize())
                # Add liked key-value to serialized data
                serialized[index]["liked"] = False
    else:
        # Serialize posts
        serialized = [post.serialize() for post in posts]

    return JsonResponse({"content": serialized, "pages": pages}, safe=False)
    
def user_data(request, user_name):
    # Get logged user, if there is one
    if request.user.username: 
        try:
            logged_user = User.objects.get(pk=request.user.id)
        except User.DoesNotExist:
            return JsonResponse({"error": "User does not exists."}, status=400)
    else:
        logged_user = None

    # Get user that will be on User's Page
    try:
        user = User.objects.get(username=user_name)
    except User.DoesNotExist:
        return JsonResponse({"error": "User does not exists."}, status=400)
    
    # Send data for User's Page
    if request.method == "GET":
        # Count how many fallows user has
        try:
            follower = Follows.objects.get(user=user)
            follows = follower.follows.count()
        except Follows.DoesNotExist:
            follows = 0

        # Check if watched user is the same as logged user and find out if the user is already followed
        if logged_user:
            is_the_same = True  if user_name == logged_user.username else False
            is_followed = True if user.followers.filter(user=logged_user) else False
        # Case when user is not logged in
        else:
            is_the_same = False
            is_followed = False

        # Prepere data
        data = {
        "follows": follows,
        "followed": user.followers.count() ,
        "is_the_same": is_the_same,
        "is_followed": is_followed
        }
        return JsonResponse(data, safe=False)

    # Change user follow status
    if request.method == "PUT":
        # User can not follow himself
        if (user_name == logged_user.username):
            return JsonResponse({"error": "Can't follow/unfollow yourself."}, status=400)

        # Get action
        data = json.loads(request.body)

        # Follow user
        if data["action"] == "follow":
            try:
                follower = Follows.objects.get(user=logged_user)
            except Follows.DoesNotExist:
                follower = Follows.objects.create(user=logged_user)
            # Add user to follwed list
            follower.follows.add(user)
            return JsonResponse({"followed": user.followers.count()}, status=201)
        
        # Unfollow user
        elif data["action"] == "unfollow":
            try:
                follower = Follows.objects.get(user=logged_user)
            except:
                return JsonResponse({"error": "Unfollowing user can not be found."}, status=404)
            # Remove user from follwed list
            follower.follows.remove(user)
            return JsonResponse({"followed": user.followers.count()}, status=201)

        else:
            return JsonResponse({"error": "Wrong action."}, status=400)

@login_required
def edit_post(request, id):
    # Get logged user and the post
    try:
        user = User.objects.get(pk=request.user.id)
        post = Posts.objects.get(pk=id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)
    except Posts.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Edit post
    if request.method == "POST":       

        # Check if user is an author of the post
        if user != post.author:
             return JsonResponse({"error": "Only author of the post is allowed to edit it."}, status=404)
        
        # Content of the users post should not be empty
        data = json.loads(request.body)
        content = data["body"]
        if content.strip() == "":
            return JsonResponse({"error": "Edited content should not be empty."}, status=400)
        
        # Save changes
        post.content = content
        post.save()

        return JsonResponse({"message": "Successfully edited post."}, status=201)
    
    # Like, unlike post
    elif request.method == "PUT":
        # Get action
        data = json.loads(request.body)

        # Like
        if data["action"] == "like":
            try:
                liker = Likes.objects.get(user=user)
            except Likes.DoesNotExist:
                liker = Likes.objects.create(user=user)

            # Add post and update like status
            liker.posts.add(post)
            post.likes += 1
            post.save()
            return JsonResponse({"likes": post.likes}, status=201)
        
        # Unlike
        elif data["action"] == "unlike":
            try:
                unliker = Likes.objects.get(user=user)
            except Likes.DoesNotExist:
                return JsonResponse({"error": "Error while unliking."}, status=404)

            # Remove post and update like status
            unliker.posts.remove(post)
            post.likes -= 1
            post.save()
            return JsonResponse({"likes": post.likes}, status=201)

        else:
            return JsonResponse({"error": "Wrong action."}, status=400)
    
    else:
        return JsonResponse({"error": "POST or PUT method only."}, status=400)