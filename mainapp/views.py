from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'main/home.html')

def about(request):
    return render(request, 'main/about.html')

def discography(request):
    return render(request, 'main/discography.html')


def contact(request):
    return render(request, 'main/contact.html')
    