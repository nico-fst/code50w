from django.shortcuts import render
from django.http import HttpResponse
import random
from markdown2 import Markdown
from . import util

markdowner = Markdown()


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, name):
    entry = util.get_entry(name)
    if entry is not None:
        entry = markdowner.convert(entry)
        return render(request, "encyclopedia/entry.html", {
            "name": name,
            "inhalt": entry
        })
    else:
        return HttpResponse(f"There is no entry named '{name}' yet.", status=404)
    
def search(request):
    searched = request.GET.get('q')
    search_entry = util.get_entry(searched)
    if search_entry is not None:
        return entry(request, searched)
    else:
        matching_entries = [entry for entry in util.list_entries() if searched.lower() in entry.lower()]
        return render(request, "encyclopedia/search.html", {
            "search": searched,
            "matching_entries": matching_entries
        })

def create(request):
    if request.method == "GET":
        return render(request, "encyclopedia/create.html", {
        }) 
    else:
        title = request.POST.get('title')
        content = request.POST.get('content')

        if title not in util.list_entries():
            util.save_entry(title, content)
        else:
            return HttpResponse("This entry already exists.")

        return entry(request, title)
    
def edit(request, name):
    if request.method == "GET":
        content = util.get_entry(name)
        return render(request, "encyclopedia/edit.html", {
            "content":  content,
            "name": name
        }) 
    else:
        content = request.POST.get('content')
        util.save_entry(name, content)
        return entry(request, name)
    
def random_entry(request):
    rand_entry = random.choice(util.list_entries())
    return entry(request, rand_entry)