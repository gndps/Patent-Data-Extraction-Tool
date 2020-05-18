from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from .models import Greeting
import requests

# Create your views here.
def index(request):
    return HttpResponse('Hello from Python!')
    # return simple_upload(request)
    # return render(request, "index.html")

def teapot(request):
    r = requests.get('http://httpbin.org/status/418')
    print(r.text)
    return HttpResponse('<pre>' + r.text + '</pre>')

def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, "db.html", {"greetings": greetings})
