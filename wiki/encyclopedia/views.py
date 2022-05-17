from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from .forms import NewEntryForm
from random import randint
from markdown2 import Markdown
import re

from . import util
# Choose markdown conversion: "user" or "library"
MARKDOWN_CONVERTION = "user"

# Renders homepage
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })
    

# Renders encyclopedia entry
def entry(request, entry_name):
    # Check if entry exists and render it if so
    
    entry_text = util.get_entry(entry_name)

    if entry_text:
        # Convert text to html

        # Markdown library
        if MARKDOWN_CONVERTION == "library":
            markdowner = Markdown()
            entry_text = markdowner.convert(entry_text)

        # Users function
        else:
            entry_text = util.convert_markdown(entry_text)

        return render(request, "encyclopedia/entry.html", {
            "entry_title" : entry_name,
            "entry_text" : entry_text
        })
    
    # Render apology if entry was not found
    return render(request, "encyclopedia/apology.html", {
        "error_code" : 404,
        "error_message" : "Requested page was not found"
    })


# Search route from index page
def search(request):
    query = request.GET['q']

    # If queried entry exists redirect to it
    if util.get_entry(query):
        return HttpResponseRedirect(f"/wiki/{query}")

    # Load all entries
    entries = util.list_entries()
    matches = []

    # Check each entry and append to matches, if there is match
    for entry in entries:
        if query.upper() in entry.upper():
            matches.append(entry)

    # Render list of matches if they exist
    if matches:
        return render(request, "encyclopedia/search.html", {
            "matches" : matches
        })

    # If no match was found
    else:
        return render(request, "encyclopedia/apology.html", {
        "error_code" : 404,
        "error_message" : "Requested page was not found"
    })


def create(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)

        # Proceed if form was valid
        if form.is_valid():
            title = form.cleaned_data["title"].capitalize()
            text = form.cleaned_data["text"]

            # Check if entry already exists
            if util.get_entry(title):
                return render(request, "encyclopedia/apology.html", {
                    "error_code" : 403,
                    "error_message" : "Entry already exists"
                    })
            
            # Save entry to a file
            util.save_entry(title, text)

            return HttpResponseRedirect(f"wiki/{title}")
        else:
            # Sending back form as "form" will display data that was not correct
            return render(request, "encyclopedia/create.html", {
            "form" : form
        })
    else:
        return render(request, "encyclopedia/create.html", {
            "form" : NewEntryForm()
        })


def edit(request):
    if request.method == "POST":
        new_form = NewEntryForm(request.POST)

        # Check if form was valid
        if new_form.is_valid():
            new_name = new_form.cleaned_data["title"].capitalize()
            new_text = new_form.cleaned_data["text"]

            # Save edited entry
            util.save_entry(new_name, new_text)

            # Redirect to new entry
            return HttpResponseRedirect(f"wiki/{new_name}")

        # If form was not valid
        else:
            return render(request, "encyclopedia/edit.html", {
            "form" : new_form
            })
    else:
        # Get entry name and content
        entry_name = request.GET["entry"]
        entry_text =  util.get_entry(entry_name)

        # Populate form with data
        data = {"title" : entry_name, "text" : entry_text}
        form = NewEntryForm(data)
        
        # Render "edit" page with populated form
        return render(request, "encyclopedia/edit.html", {
            "form" : form
        })


def delete(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)

        # Check if form was valid
        if form.is_valid():
            title = form.cleaned_data["title"].capitalize()

            # Delete edited entry
            util.delete_entry(title)

    return HttpResponseRedirect("/", {
        "entries" : util.list_entries()
        })


def random(request):
    # Get list of all entries
    entries = util.list_entries()

    # Get a random index
    index = randint(0, len(entries) - 1)

    # Redirect to random entry
    random_title = entries[index]
    return HttpResponseRedirect(f"/wiki/{random_title}")