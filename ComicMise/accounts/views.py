import random
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import RegistrationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from .helper import MessageHandler
from django.utils.decorators import method_decorator
from uuid import uuid4
from django.urls import reverse
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
#Model importing
from store.models import Product, ProductImage, ProductVariation
from category.models import Category
from .models import Account, Profile, Address

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
class register(View):
    @method_decorator(no_cache)
    def get(self,request):
        form = RegistrationForm()
        context = {
            'form':form
        }
        return render(request,'greatkart/register.html',context)

    @method_decorator(no_cache)
    def post(self,request):
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
                
        
class otpVerify(View):
    @method_decorator(no_cache)
    def get(self,request,pk):
        profile=Profile.objects.get(pk=pk)
        return render(request,'greatkart/otp.html',{'id':pk,'profile':profile})
    
    @method_decorator(no_cache)
    def post(self,request,pk):
        profile=Profile.objects.get(pk=pk)  
        user = get_object_or_404(Account, pk=profile.user_id)    
        if request.COOKIES.get('can_otp_enter')!=None:
            if(profile.otp==request.POST['otp']):
                user.is_active=True
                user.is_user=True
                user.save()
                print(user.is_active,user.is_admin, user.is_user,user.username,profile.id)
                request.session['user_id'] = user.id
                red=redirect('home')
                red.set_cookie('verified',True)
                auth_login(request, user)
                return red
            messages.info(request, 'Wrong OTP. Please try again')   
        messages.info(request, 'Times out. Please try again')         
        
class resend_otp(View):
    @method_decorator(no_cache)
    def post(self,request,pk):
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



class logout(View):
    @login_required(login_url='login')
    def post(self,request):
        logout(request)
        return redirect('login')

class home(View):
    def get(self,request):
        
        #user_id = Account.objects.get(pk=pk)
        products = Product.objects.all().filter(is_available=True)
        user_id = request.session['user_id'] 
        print(user_id)
        user = get_object_or_404(Account, pk=user_id)
        print(user.username)
        context = {
            'products': products,
            'user_name': user.username,
        }
        return render(request, 'home.html', context)

class store(View):
    def get(self,request, category_slug=None):
        category = None
        products = None
        user_id = request.session['user_id']
        user = Account.objects.get(pk=user_id)
        username = user.username

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
            'user_name': username,
        }
        return render(request, 'greatkart/store.html', context)

class product_detail(View):   
    def get(self,request, category_slug, product_slug, size):
        print(size)
        user_id = request.session['user_id']
        user = Account.objects.get(pk=user_id)

        print(user_id)
        print(user)
        print(user.id)
        username = user.username
        try:
            single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
            images = ProductImage.objects.filter(product=single_product)
            variant = ProductVariation.objects.get(product=single_product, size=size)
            print(variant)
            print(variant.id)
        except Exception as e:
            raise e
        context = {
            'single_product': single_product,
            'images':images,
            'user_id':user_id,
            'user_name': username, 
            'variant':variant.id, 
            'stock':variant.stock,
            'category_slug':category_slug,
            'product_slug':product_slug
        }
        return render(request,'greatkart\product_detail.html',context)
    

class userProfile(View):
    def get(self, request, user_name):
        user_id = request.session['user_id']
        user = Account.objects.get(pk=user_id)
        username = user.username
        addresses = user.addresses.all()
        context={
            'user':user,
            'user_name': username,
            'addresses': addresses
        }
        return render(request, 'evara-frontend/page-account.html', context)

    def post(self,request, user_name):
        form_id = request.POST.get('form_identifier')
        print(form_id)

        #checking form......
        if form_id == 'add address':
            address_title    = request.POST['address_title']
            name             = request.POST['name']
            ph_number        = request.POST['ph_number']
            pincode          = request.POST['pincode']
            locality         = request.POST['locality']
            address          = request.POST['address']
            city             = request.POST['city']
            state            = request.POST['state']
            landmark         = request.POST['landmark']
            alt_phone_number = request.POST['alt_phone_number']

             #checking.....
            if not address_title or not ph_number or not pincode or not address or not locality or not city or not state or not name:
                messages.error(request,'Enter the required fields')
                return redirect('userProfile', user_name=user_name )

            fd = Address(address_title=address_title, name=name, ph_number=ph_number, pincode=pincode, locality=locality, address=address, city=city, state=state, landmark=landmark, alt_phone_number=alt_phone_number)
            fd.save()
            
            user_name=user_name
            user_id = request.session['user_id']
            user = Account.objects.get(pk=user_id)
            user.addresses.add(fd)
            return redirect('userProfile', user_name=user_name)
    