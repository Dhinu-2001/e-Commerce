import random
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import RegistrationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .helper import MessageHandler
from django.utils.decorators import method_decorator
from uuid import uuid4
from django.urls import reverse
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
#For link verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


#Model importingfrom django.
from store.models import Product, ProductImage, ProductVariation
from category.models import Category
from .models import Account, Profile, Address
from cart.models import Order, OrderItem
from wallet.models import Wallet

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
        return render(request,'reid/registration.html',context)

    
    def post(self,request):
        form =RegistrationForm(request.POST)
        verification_option = request.POST.get('verification_option')
        print(verification_option)
        if verification_option is None: 
            print(1)
            messages.error(request, 'Please choose one of the verification method.')
            return redirect('register')
        else:
            if form.is_valid():
                first_name=form.cleaned_data['first_name']
                last_name=form.cleaned_data['last_name']
                phone_number=form.cleaned_data['phone_number']
                email=form.cleaned_data['email']
                password=form.cleaned_data['password']
                username=email.split('@')[0]
                if not first_name or not last_name or not phone_number or not email or not password:
                    messages.error(request, 'Please, enter the required fields')
                    return redirect('register')
                user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
                print(2)
                if verification_option  == 'OTP':
                    user.phone_number=phone_number
                    user.save()
                    otp=random.randint(1000,9999)
                    profile=Profile.objects.create(user=user, phone_number=phone_number, otp=f'{otp}')
                    messagehandler=MessageHandler( phone_number, otp).send_otp_via_message()
                    # profile.uid = uuid4()
                    expiry_time = datetime.now() + timedelta(minutes=2)
                    profile.otp_expiry = expiry_time
                    red=redirect('otp', pk=profile.pk)
                    # red=redirect(f'/accounts/otp/{profile.uid}/')
                    red.set_cookie("can_otp_enter", True, max_age=120)
                    return red 
                elif verification_option == 'EMAIL_LINK':
                    print(3)
                    current_site = get_current_site(request)
                    mail_subject = 'Please activate your account'
                    message = render_to_string('reid/link_verification.html',{
                        'user':user,
                        'domain': current_site,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token' : default_token_generator.make_token(user),
                    })
                    to_email = email
                    send_email = EmailMessage(mail_subject, message, to=[to_email])
                    send_email.send()
                    print('sent')
                    #messages.success(request, 'Thank you for registering with us. We have sent you a verification email to your email address.Please verify it.')
                    return redirect('/accounts/login/?command=verification&email='+email)
                else:
                    print(4)
                    # Handle other verification options here
                    # For example, you might want to return a different HttpResponse or redirect
                    return redirect('register')
            else:
                context = {
                    'form':form
                }
                return render(request,'reid/registration.html',context)
        
class otpVerify(View):
    @method_decorator(no_cache)
    def get(self,request,pk):
        profile=Profile.objects.get(pk=pk)
        return render(request,'reid/otp.html',{'id':pk,'profile':profile})
      
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
    def get(self,request,pk):
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
    
class link_verification(View):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = Account._default_manager.get(pk=uid)
        except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
            user = None
        
        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.is_user=True
            user.save()
            messages.success(request, 'Congratulations! Your account is activated.')
            return redirect('login')

class Login(View):
    def get(self,request):
        return render(request,'reid/login.html')
    
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not email or not password:
            messages.error(request, 'Enter email and password')
            return render(request, 'reid/login.html')
        print(email , password)
        user = authenticate(request, email=email, password=password)
        if user is not None:
            if user.is_active:
                print(user.is_active, user.is_admin, user.is_user)
                # Check user permissions
                if user.is_admin:
                    # User is an admin
                    request.session['user_id'] = user.id
                    auth_login(request, user)
                    return redirect('adminDashboard')
                elif user.is_user:
                    # User is a regular user
                    print(request.session.keys())   
                    request.session['user_id'] = user.id
                    red=redirect('home')#, pk=user.pk
                    auth_login(request, user)
                    return red
            else:
                print('not activated')
                messages.error(request, 'Your account is inactive.')
        else:
            print('not authenticated')
            messages.error(request, 'Invalid login details supplied.')
        return render(request, 'reid/login.html')
    
class forgotPassword(View):
    def get(self, request):
        return render(request, 'reid/forgotPassword.html')

    def post(self, request):
        email = request.POST.get('email')
        if Account.objects.filter(email = email).exists():
            user = Account.objects.get(email__exact = email)
            # Reset Password===================================
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('reid/reset_password_email.html',{
                'user':user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            print('sent')
            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')
        
class resetpassword_validate(View):
    def get(self, request , uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = Account._default_manager.get(pk=uid)
        except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
            user = None
        
        if user is not None and default_token_generator.check_token(user, token):
            request.session['uid'] = uid
            messages.success(request, 'Please reset your password')
            return redirect('resetPassword')
        else:
            messages.error(request, 'This link has been expired')
            return redirect('login')
        
class resetPassword(View):
    def get(self,request):
        return render(request, 'reid/resetPassword.html')
    def post(self, request):
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk = uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        elif password != confirm_password:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
        else:
            messages.error(request, 'Password must be length of 8, must contain an uppercase, lowercase, atleast an integer and a special symbol')
            return redirect('resetPassword')

@method_decorator(login_required(login_url='login'), name='dispatch')
class logout(View):
    def get(self,request):
        if request.user.is_authenticated:
            auth_logout(request)
            messages.success(request, 'You are logged out.')
        return redirect('login')


@method_decorator(login_required(login_url='login'), name='dispatch')
class userProfile(View):
    def get(self, request, user_name):
        user_id = request.session.get('user_id')  # Use get method to avoid KeyError
        user = None  # Initialize user to None

        if user_id is not None:  # Check if user_id exists
            user = get_object_or_404(Account, pk=user_id)

        username = user.username
        addresses = user.addresses.all()
        try:
            wallet = Wallet.objects.get(user = user)
        except Wallet.DoesNotExist:
            wallet = Wallet.objects.create(user = user)
            
        print(wallet)
        wallet.save()

#---------------------------------------------------------------- Order details
        
        total_price=[]
        orders = Order.objects.filter(user = user).order_by('-order_date')
        # for order in orders:
        #     total_price = order.calculate_total_price()
          
        context={
            'user_id':user_id,
            'user': user,
            'addresses': addresses,
            'orders':orders,
            'wallet':wallet
            # 'total_price':total_price,
        }
        return render(request, 'reid/my-account.html', context)

@method_decorator(login_required(login_url='login'), name='dispatch')
class userside_order_detail(View):
    def get(self, request, order_id):
        user_id = request.session.get('user_id')  # Use get method to avoid KeyError
        user = None  # Initialize user to None

        if user_id is not None:  # Check if user_id exists
            user = get_object_or_404(Account, pk=user_id)


        order = Order.objects.get(id = order_id)
        order_items = OrderItem.objects.filter(order=order)
        context ={
            'user_id':user_id,
            'user': user,
            'order':order,
            'order_items':order_items,

        }
        return render(request, 'reid/order_detail.html',context)

@method_decorator(login_required(login_url='login'), name='dispatch')
class cancel_order(View):
    def get(self, request, order_id):
        user_id = request.session.get('user_id')  # Use get method to avoid KeyError
        user = None  # Initialize user to None

        if user_id is not None:  # Check if user_id exists
            user = get_object_or_404(Account, pk=user_id)

        order = Order.objects.get(id = order_id)
        order.canceled = True
        order.save()
        if order.payment_method != 'CASH_ON_DELIVERY':
            try:
                wallet = Wallet.objects.get(user = user)
                print(wallet)
            except Wallet.DoesNotExist:
                wallet = Wallet.objects.create(user = user)
                print(wallet)
                wallet.save()
            total_price = order.total_price
            wallet.amount += total_price
            wallet.save()        
        return redirect('userside_order_detail', order_id=order_id)

@method_decorator(login_required(login_url='login'), name='dispatch') 
class add_address(View):
    def get(self, request):
        return render(request, 'reid/add_address.html')
    
    def post(self, request):
        user_id = request.session.get('user_id')  # Use get method to avoid KeyError
        user = None  # Initialize user to None
        if user_id is not None:  # Check if user_id exists
            user = get_object_or_404(Account, pk=user_id)

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
    # FORM VALIDATION===============================================
    # CHECKING MANDATORY FIELDS
        if not address_title or not name or not ph_number or not pincode or not locality or not address or not city or not state:
            messages.error(request,'Please, enter the required fields')
            return redirect('add_address')
        
    # CHECKING PHONE NUMBERS
        if ph_number:
            if not ph_number.isdigit():
                messages.error(request,'Give valid phone number.(Phone number should be integers)')
                return redirect('add_address')
            elif len(ph_number) != 10:
                messages.error(request,'Give valid phone number.(Phone number should contain 10 digits)')
                return redirect('add_address')
            elif len(set(ph_number)) == 1 and ph_number[0] == '0':
                messages.error(request, "Phone number can't contain only 0s ")
                return redirect('add_address')
        if alt_phone_number:
            if not alt_phone_number.isdigit():
                messages.error(request,'Give valid phone number.(Phone number should be integers)')
                return redirect('add_address')
            elif len(alt_phone_number) != 10:
                messages.error(request,'Give valid phone number.(Phone number should contain 10 digits)')
                return redirect('add_address')
            elif len(set(alt_phone_number)) == 1 and alt_phone_number[0] == '0':
                messages.error(request, "Phone number can't contain only 0s ")
                return redirect('add_address')
    # CHECKING PINCODE
        if pincode:
            if not pincode.isdigit():
                messages.error(request,'Give valid phone number.(Pin code should be integers)')
                return redirect('add_address')
            elif len(pincode) != 6:
                messages.error(request,'Give valid phone number.(Pin code should contain 6 digits)')
                return redirect('add_address')
            elif len(set(pincode)) == 1 and pincode[0] == '0':
                messages.error(request, "Pin code can't contain only 0s ")
                return redirect('add_address')
    # CHECKING LOCALITY
        if any(char.isdigit() for char in locality):
            messages.error(request,"Locality name should not contain numbers")
            return redirect('add_address')
    # CHECKING CITY
        if any(char.isdigit() for char in city):
            messages.error(request,"City name should not contain numbers")
            return redirect('add_address')
    # CHECKING STATE
        if any(char.isdigit() for char in state):
            messages.error(request,"State name should not contain numbers")
            return redirect('add_address')
        
        fd = Address(address_title=address_title, name=name, ph_number=ph_number, pincode=pincode, locality=locality, address=address, city=city, state=state, landmark=landmark, alt_phone_number=alt_phone_number)
        fd.save()
        user.addresses.add(fd)
        return redirect('userProfile', user_name=user.username)


@method_decorator(login_required(login_url='login'), name='dispatch') 
class edit_address(View):
    def get(self, request, address_id):
        user_id = request.session.get('user_id')  # Use get method to avoid KeyError
        user = None  # Initialize user to None

        if user_id is not None:  # Check if user_id exists
            user = get_object_or_404(Account, pk=user_id)

        address = Address.objects.get(id = address_id)
        context={
            'user_id':user_id,
            'user': user,
            'address':address,
        }
        return render(request, 'reid/edit_address.html', context)
    
    def post(self, request, address_id):
        user_id = request.session.get('user_id')  # Use get method to avoid KeyError
        user = None  # Initialize user to None
        if user_id is not None:  # Check if user_id exists
            user = get_object_or_404(Account, pk=user_id)
        
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
# FORM VALIDATION===============================================
        # CHECKING MANDATORY FIELDS
        if not address_title or not name or not ph_number or not pincode or not locality or not address or not city or not state:
            messages.error(request,'Please, enter the required fields')
            return redirect('edit_address', address_id=address_id)

            
        # CHECKING PHONE NUMBERS
        if ph_number:
            if not ph_number.isdigit():
                messages.error(request,'Give valid phone number.(Phone number should be integers)')
                return redirect('edit_address', address_id=address_id)
            elif len(ph_number) != 10:
                messages.error(request,'Give valid phone number.(Phone number should contain 10 digits)')
                return redirect('edit_address', address_id=address_id)
            elif len(set(ph_number)) == 1 and ph_number[0] == '0':
                messages.error(request, "Phone number can't contain only 0s ")
                return redirect('edit_address' , address_id=address_id)
        if alt_phone_number:
            if not alt_phone_number.isdigit():
                messages.error(request,'Give valid phone number.(Phone number should be integers)')
                return redirect('edit_address', address_id=address_id)
            elif len(alt_phone_number) != 10:
                messages.error(request,'Give valid phone number.(Phone number should contain 10 digits)')
                return redirect('edit_address', address_id=address_id)
            elif len(set(ph_number)) == 1 and ph_number[0] == '0':
                messages.error(request, "Phone number can't contain only 0s ")
                return redirect('edit_address' , address_id=address_id)
        # CHECKING PINCODE
        if pincode:
            if not pincode.isdigit():
                messages.error(request,'Give valid pin code.(Pin code should be integers)')
                return redirect('edit_address', address_id=address_id)
            elif len(pincode) != 6:
                messages.error(request,'Give valid pin code.(Pin code should contain 6 digits)')
                return redirect('edit_address', address_id=address_id)
            elif len(set(pincode)) == 1 and pincode[0] == '0':
                messages.error(request, "Pin code can't contain only 0s ")
                return redirect('edit_address' , address_id=address_id)
    # CHECKING LOCALITY
        if any(char.isdigit() for char in locality):
            messages.error(request,"Locality name should not contain numbers")
            return redirect('edit_address' , address_id=address_id)
    # CHECKING CITY
        if any(char.isdigit() for char in city):
            messages.error(request,"City name should not contain numbers")
            return redirect('edit_address' , address_id=address_id)
    # CHECKING STATE
        if any(char.isdigit() for char in state):
            messages.error(request,"State name should not contain numbers")
            return redirect('edit_address' , address_id=address_id)

        address_inst = Address.objects.get(id = address_id)
        address_inst.address_title = address_title
        address_inst.name = name 
        address_inst.ph_number = ph_number
        address_inst.pincode = pincode
        address_inst.locality = locality
        address_inst.address = address
        address_inst.city = city
        address_inst.state = state
        if landmark:
            address_inst.landmark = landmark
        elif alt_phone_number:
            address_inst.alt_phone_number = alt_phone_number
        else:
            pass
        address_inst.save()
        print('end')
        return redirect('userProfile', user_name=user.username)

@method_decorator(login_required(login_url='login'), name='dispatch') 
class delete_address(View):
    def get(self, request, address_id):
        user_id = request.session.get('user_id')  # Use get method to avoid KeyError
        user = None  # Initialize user to None

        if user_id is not None:  # Check if user_id exists
            user = get_object_or_404(Account, pk=user_id)

        address = Address.objects.get(id = address_id)
        address.delete()
        return redirect('userProfile', user_name=user.username)
    
# FOR EMAIL VALIDATION ==========================
import re
from django.shortcuts import render

def validate_email(email):
    # Regular expression pattern for email validation
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)
#=================================================

@method_decorator(login_required(login_url='login'), name='dispatch') 
class edit_account_details(View):
    def get(self, request, user_name):
        user_id = request.session.get('user_id')  # Use get method to avoid KeyError
        user = None  # Initialize user to None

        if user_id is not None:  # Check if user_id exists
            user = get_object_or_404(Account, pk=user_id)
        context={
            'user_id':user_id,
            'user': user,
        }
        return render(request, 'reid/edit_account_detail.html', context)
    
    def post(self, request, user_name):
        user_id = request.session.get('user_id')  # Use get method to avoid KeyError
        user = None  # Initialize user to None

        if user_id is not None:  # Check if user_id exists
            user = get_object_or_404(Account, pk=user_id)
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        email = request.POST.get('email-name')
        ph_number = request.POST.get('phone-number')
    
    # VALIDATION ===============================================
        errors = {}
        if ' ' in set(first_name) and len(set(first_name)) == 1:
            errors['first_name'] ="First name cannot contain only white space"
        if any(first_name[i] == first_name[i+1] == first_name[i+2] for i in range(len(first_name)-2)):
            errors['first_name'] ="First name cannot contain consecutive three same letters."
        if any(char.isdigit() for char in first_name):
            errors['first_name'] ="First name cannot contain digits."
        if '.' in first_name:
            errors['first_name'] ="First name cannot contain dots."
        if len(first_name) <= 2:
            errors['first_name'] ="First name must be longer than 2 characters."

        if ' ' in set(last_name) and len(set(last_name)) == 1:
            errors['last_name'] ="Last name cannot contain only white space"
        if any(last_name[i] == last_name[i+1] == last_name[i+2] for i in range(len(last_name)-2)):
            errors['last_name'] ="Last name cannot contain consecutive three same letters."
        if any(char.isdigit() for char in last_name):
            errors['last_name'] ="Last name cannot contain digits."
        if '.' in last_name:
            errors['last_name'] ="Last name cannot contain dots."

        if not validate_email(email):
            errors['email'] = 'Invalid email address.'

        if not ph_number.isdigit():
            print(type(ph_number), ph_number)
            errors['phone_number'] ='Phone number must contain only digits.'
        elif len(ph_number) != 10:
            errors['phone_number'] ='Phone number must be exactly 10 digits.'
        elif len(set(ph_number)) == 1 and ph_number[0] == '0':  # Compare as a string
            errors['phone_number'] ="Phone number can't contain only 0s."
        
        if errors:
            context={
                'errors':errors,
            }
            return render(request, 'reid/edit_account_detail.html', context)
        
        else:   
            user_inst = Account.objects.get(id = user_id)

            user_inst.first_name = first_name
            user_inst.last_name = last_name
            user_inst.email = email
            user_inst.phone_number = ph_number
            user_inst.save()

            return redirect('userProfile', user_name=user.username)
        

@method_decorator(login_required(login_url='login'), name='dispatch') 
class change_password(View):
    def get(self, request):
        user_id = request.session.get('user_id')  # Use get method to avoid KeyError
        user = None  # Initialize user to None

        if user_id is not None:  # Check if user_id exists
            user = get_object_or_404(Account, pk=user_id)
        context={
            'user_id':user_id,
            'user': user,
        }
        return render(request, 'reid/change_password.html',context)
    
    def post(self, request):
        user_id = request.session.get('user_id')  # Use get method to avoid KeyError
        user = None  # Initialize user to None

        if user_id is not None:  # Check if user_id exists
            user = get_object_or_404(Account, pk=user_id)
        
        current_pass = request.POST.get('current_password')
        new_pass = request.POST.get('new_password')
        confirm_pass = request.POST.get('confirm_password')

        if not current_pass or not new_pass or not confirm_pass:
            messages.error(request, 'Enter all the required fields.')
        errors={}
        #user = Account.objects.get(username__exact=request.user.username)
        if not user.check_password(current_pass):
            errors['current_pass'] ='Current password does not match.'
        if new_pass:
            if len(new_pass) < 8:
                errors['new_pass'] ="Password must be at least 8 characters long."
            # Check if password contains at least one digit
            if not any(char.isdigit() for char in new_pass):
                errors['new_pass'] ="Password must contain at least one numeric character."
            # Check if password contains at least one uppercase letter
            if not any(char.isupper() for char in new_pass):
                errors['new_pass'] ="Password must contain at least one uppercase letter."
            # Check if password contains at least one lowercase letter
            if not any(char.islower() for char in new_pass):
                errors['new_pass'] ="Password must contain at least one lowercase letter."
            # Check if password contains at least one special character
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_pass):
                errors['new_pass'] ="Password must contain at least one special character."
            # Check for whitespaces in the password
            if ' ' in new_pass:
                errors['new_pass'] ="Password cannot contain whitespaces."
        if confirm_pass:
            if new_pass != confirm_pass:
                errors['confirm_pass'] ="Passwords do not match."
        
        if errors:
            context={
                'errors':errors,
                'user_id':user_id,
                'user': user,
            }
            return render(request,  'reid/change_password.html', context)
        
        else:
            user.set_password(new_pass)
            user.save()
            auth_logout(request)
            messages.success( request, "Password updated successsfully. Please login again" )
            return redirect('login')
            
        