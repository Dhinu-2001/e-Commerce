from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login as auth_login
from accounts.models import Account
from category.models import Category
from store.models import Product
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

def categoryView(request):
    if request.method == 'POST':
        cat_name =request.POST['category_name']
        cat_description =request.POST['category_description']
        cat_image = request.FILES.get('category_image')
        
        if not cat_name or not cat_description :# or not cat_image
            messages.error(request,'Enter all fields')
            return redirect ('categoryView')
        fd = Category(category_name=cat_name, description = cat_description, cat_image= cat_image) 
        fd.save()
        return redirect('categoryView')
    else:
        category_set = Category.objects.all()
        context = {
            'category_set': category_set,
        }
    return render(request,'evara-backend/page-categories.html', context)


def add_product(request):
    if request.method == 'POST':
        prod_name        = request.POST['product_name']
        prod_description = request.POST['product_description']
        prod_price       = request.POST['product_price']
        prod_image       = request.FILES.get('product_image')
        prod_category    = request.POST.get('product_category')
        prod_stock       = request.POST.get('product_stock')
  
        # print(prod_name,prod_description,prod_price,prod_category,prod_stock)
        
        if not prod_name or not prod_description or not prod_price or not prod_image or not prod_stock or not prod_category:
            messages.error(request,'Enter the required fields')
            return redirect('add_product')
        
        #getting category using primary key
        cat_key= Category.objects.get_primary_key_by_name(prod_category)
        exact_category = Category.objects.get(pk=cat_key)
        print(prod_name,prod_description,prod_price,prod_stock ,prod_category, cat_key, exact_category)
        
        fd = Product(product_name=prod_name, description=prod_description, price=prod_price, stock= prod_stock, category = exact_category, images=prod_image )
        fd.save()
        return redirect('add_product')
    
    category_list = Category.objects.all()
    context = {
        'category_list': category_list
    }
    return render(request,'evara-backend/page-form-product-1.html', context)


def customers_list(request):
    user_set = Account.objects.all()
    return render(request,'evara-backend/page-customers-list.html',{'userlist':user_set})