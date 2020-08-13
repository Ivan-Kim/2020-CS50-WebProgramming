from django.shortcuts import render
from django.http import HttpResponseRedirect
from django import forms
from django.urls import reverse
from django.contrib import messages
from django.utils.safestring import mark_safe

from . import util

import markdown2, random

class newWikiForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(label="Add Content", widget=forms.Textarea)

def index(request):
    wordList = util.list_entries()
    query = request.GET.get("q", "")
    # if use search bar
    if query in wordList:
        return show(request, query)
    else:
        return render(
            request,
            "encyclopedia/index.html",
            # when no query, return main page. if query does not match, return guess page
            {
                "entries": wordList
                if not query
                else [s for s in wordList if query in s],
                "query": query,
            },
        )


def show(request, name):
    # show random results if 'Random Page' at side bar clicked
    if name == "random":
        wordList = util.list_entries()
        randomNum = random.randint(0, len(wordList) - 1)
        randomWord = wordList[randomNum]
        return show(request, randomWord)
    return render(
        request,
        "encyclopedia/result.html",
        {
            "name": name,
            "result": (markdown2.markdown(util.get_entry(name)))
            if util.get_entry(name)
            else None,
        },
    )


def randomShow(request):
    wordList = util.list_entries()
    randomNum = random.randint(0, len(wordList) - 1)
    randomWord = wordList[randomNum]
    return show(request, randomWord)


def new(request):
    # if user submits new title and content
    if request.method == "POST":
        form = newWikiForm(request.POST)
        if form.is_valid():
            new_title = form.cleaned_data["title"]
            new_content = form.cleaned_data["content"]
            # if title is new save it in database and redirect to its wiki page
            if not util.get_entry(new_title):
                util.save_entry(new_title, new_content)
                return HttpResponseRedirect(f"{new_title}")
            # if title is already in entries print error
            else:
                messages.error(request, "Entry already exists (Close popup message to reset)")
                return render(request, "encyclopedia/newpage.html", {"form": form})
        # if form not valid stay
        else:
            return render(request, "encyclopedia/newpage.html", {"form": form})
    # if accessed through left tab 'Create New Page' link
    return render(request, "encyclopedia/newpage.html", {"form": newWikiForm()})

def edit(request):
    # default edit page
    if request.method == "GET":
        edit_title = request.GET.get("title", "")
        md_content = util.get_entry(edit_title)
        return render(request, "encyclopedia/edit.html", {"form": newWikiForm(initial={"title": edit_title, "content": md_content})})
    # update edit page
    elif request.method == "POST":
        form = newWikiForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            edited_content = form.cleaned_data["content"]
            util.save_entry(title, edited_content)
            return HttpResponseRedirect(f"{title}")
