from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def index(request):
    return render(request, "index.html")


def profile(request):
    return render(request, "profile.html")


def login(request):
    return render(request, "login.html")


def signup(request):
    return render(request, "signup.html")

def receiveToken(request):
	#return HttpResponse(request)
	return render(request, "profile.html")

