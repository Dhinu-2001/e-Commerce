import random
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from .helper import MessageHandler
from uuid import uuid4
from django.urls import reverse
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
#Model importing
from store.models import Product, ProductImage, ProductVariation
from category.models import Category
from .models import Account, Profile

# Create your views here.
#================================no cache decorator===============================================
def no_cache(view_func):
    """
    Decorator to add no-cache headers to a view function.
    """
    @never_cache
    def _wrapped_view(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    return _wrapped_view
#================================no cache decorator===============================================
@no_cache
def register(request):
    if request.method == 'POST':
        form =RegistrationForm(request.POST)
        if form.is_valid():
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            phone_number=form.cleaned_data['phone_number']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            username=email.split('@')[0]

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            otp=random.randint(1000,9999)
            user.phone_number=phone_number
            user.save()
            profile=Profile.objects.create(user=user, phone_number=phone_number, otp=f'{otp}')
            messagehandler=MessageHandler( phone_number, otp).send_otp_via_message()
            # profile.uid = uuid4()
            expiry_time = datetime.now() + timedelta(minutes=2)
            profile.otp_expiry = expiry_time
            red=redirect('otp', pk=profile.pk)
            # red=redirect(f'/accounts/otp/{profile.uid}/')

            red.set_cookie("can_otp_enter", True, max_age=120)
            return red  
            # otp_url = reverse('otp', kwargs={'uid': profile.uid})
            # otp_full_url = request.build_absolute_uri(otp_url)

            # Redirect to the OTP verification URL
            # red = redirect(otp_full_url)
            # red.set_cookie("can_otp_enter", True, max_age=600)
            # return red

            # messages.success(request, 'Registration successful.')
            # return redirect('register')
    else:
        form = RegistrationForm()
    context = {
        'form':form
    }
    return render(request,'greatkart/register.html',context)

@no_cache
def otpVerify(request,pk):
    profile=Profile.objects.get(pk=pk)
    if request.method=="POST":  
        user = Account.objects.get(username = profile.user.username)    
        if request.COOKIES.get('can_otp_enter')!=None:
            if(profile.otp==request.POST['otp']):
                red=redirect('home')
                red.set_cookie('verified',True)
                auth_login(request, user)
                return red
            messages.info(request, 'Wrong OTP. Please try again')   
        messages.info(request, 'Times out. Please try again')         
    return render(request,'greatkart/otp.html',{'id':pk,'profile':profile})

@no_cache
def resend_otp(request,pk):
    # Here, implement the logic to resend the OTP
    # You can use your MessageHandler class to send the OTP
    # Assuming you have access to the phone number of the user who needs to resend OTP
    profile = Profile.objects.get(pk=pk)  # Adjust this to fetch the phone number from your profile model
    
    # Generate a new OTP
    new_otp = random.randint(1000, 9999)
    expiry_time = datetime.now() + timedelta(minutes=2)
    profile.otp_expiry = expiry_time
    profile.otp=new_otp # And Optionally, you can update the profile with the new OTP
    profile.save()


    # Send the new OTP via message
    message_handler = MessageHandler(profile.phone_number, new_otp)
    message_handler.send_otp_via_message()

    # Return a JSON response indicating success
    red=redirect('otp', pk=profile.pk)
    red.set_cookie("can_otp_enter", True, max_age=120)
    return red


# @no_cache
# def login(request):
#     if request.method == 'POST':
#         email = request.POST['email']
#         password = request.POST['password']
#         if not email or not password:
#             messages.error(request,'Enter email and password')
#             return render(request,'greatkart/signin.html')
#         print(email , password)
#         user = authenticate(request, email=email, password=password)
#         print(user)
#         if user is not None:
#             auth_login(request, user)
#             return redirect('home')
#         else:
#             messages.error(request, 'Invalid login credentials')
#             return redirect('login')
#     return render(request,'greatkart/signin.html')


@login_required(login_url='login')
def logout(request):
    logout(request)
    return redirect('login')

def home(request):
    products = Product.objects.all().filter(is_available=True)

    context = {
        'products': products,
    }
    return render(request, 'home.html', context)

def store(request, category_slug=None):
    category = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        prod_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True)
        prod_count = products.count()
        category = Category.objects.all()
    context = {
        'products': products,
        'prod_count': prod_count,
        'category': category,
    }
    return render(request, 'greatkart/store.html', context)
    
def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        images = ProductImage.objects.filter(product=single_product)
       
    except Exception as e:
        raise e
    context = {
        'single_product': single_product,
        'images':images,
        
    }
    return render(request,'greatkart/product_detail.html',context)