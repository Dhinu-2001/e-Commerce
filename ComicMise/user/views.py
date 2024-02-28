from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login as auth_login

from django.http import HttpResponse
from django.contrib import messages
# Create your views here.

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not email or not password:
            messages.error(request,'Enter email and password')
            return render(request,'evara-backend/page-account-login.html')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            if user.is_active:
                # Check user permissions
                if user.is_superadmin:
                    # User is a superadmin
                    request.session['user_id']=user.id
                    auth_login (request, user)
                    return redirect('adminDashboard')
                elif user.is_staff:
                    # User is a staff member
                    login(request, user)
                    return HttpResponse('You are logged in as staff.')
                elif user.is_admin:
                    # User is an admin
                    login(request, user)
                    return HttpResponse('You are logged in as admin.')
            else:
                messages.error(request, 'Your account is inactive.')
        else:
            messages.error(request, 'Invalid login details supplied.')
    return render(request,'evara-backend/page-account-login.html')

def home(request):
    return render(request,'home.html')

def adminDashboard(request):
    return render(request,'evara-backend/index.html')

def category(request):
    return render(request,'evara-backend/page-categories.html')

def customers_list(request):
    return render(request,'evara-backend/page-customers-list.html')