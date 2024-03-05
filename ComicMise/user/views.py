from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login as auth_login
#Import Models
from accounts.models import Account
from category.models import Category
from store.models import Product, ProductImage, ProductVariation


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
    products = Product.objects.all().filter(is_available=True)

    context = {
        'products': products,
    }
    return render(request, 'home.html', context)

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

def product_list(request):
    productlist = Product.objects.all()
  
    context={
        'productlist': productlist
        
    }
    return render(request,'evara-backend/page-products-list.html', context)

def add_product(request):
    if request.method == 'POST':
        prod_name        = request.POST['product_name']
        prod_description = request.POST['product_description']
        prod_price       = request.POST['product_price']
        prod_cat_slug    = request.POST.get('product_category')
        prod_size        = request.POST.get('product_size')
        prod_stock       = request.POST.get('product_stock')
        prod_images      = [request.FILES.get('image1'), request.FILES.get('image2'), request.FILES.get('image3')]
  
        
        #checking.....
        if not prod_name or not prod_description or not prod_price or not prod_stock or not prod_cat_slug or not prod_size:
            messages.error(request,'Enter the required fields')
            return redirect('add_product')
        
        #getting category-Instanse using primary key
        category_inst=Category.objects.get(slug=prod_cat_slug)
        

        if len(prod_images) == 3 and all(prod_images):
            fd = Product(product_name=prod_name, description = prod_description, price= prod_price, category=category_inst) 
            fd.save()

            #getting Instance
            product_inst = Product.objects.get(product_name=prod_name)
            # size_inst    = SizeVariant.objects.get(size=prod_size)

            variation = ProductVariation.objects.filter(product=product_inst, size=prod_size)
            
            if variation:
            # If the variation exists, update the stock_quantity
                variation.stock += prod_stock
                variation.save()
            else:
            # If the variation doesn't exist, create a new entry
                ProductVariation.objects.create(product=product_inst, size=prod_size, stock=prod_stock)
                # variation.save()
            for img in prod_images:
                ProductImage.objects.create(product=product_inst, image=img)    
            return redirect('product_list')
        else:
            messages.error(request,'Please upload 3 images.')
            return redirect('add_product')
                    
        # return redirect('product_detail', product_id=product_id)
            
    category_list = Category.objects.all()
    
    context = {
        'category_list': category_list
        
    }
    return render(request,'evara-backend/page-form-product-1.html', context)

def product_detail(request):
    return render(request,'evara-backend/product-detail.html')

def customers_list(request):
    user_set = Account.objects.all()
    return render(request,'evara-backend/page-customers-list.html',{'userlist':user_set})