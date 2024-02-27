from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request,'home.html')
def category(request):
    return render(request,'evara-backend/page-categories.html')