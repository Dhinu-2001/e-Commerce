from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login as auth_login
from django.views import View
from django.utils.decorators import method_decorator
#Import Models
from accounts.models import Account
from category.models import Category
from store.models import Product, ProductImage, ProductVariation
from cart.models import Order, OrderItem


from django.http import HttpResponse
from django.contrib import messages
# Create your views here.

class Login(View):
    def get(self,request):
        
        return render(request,'greatkart/signin.html')
    
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not email or not password:
            messages.error(request, 'Enter email and password')
            return render(request, 'greatkart/signin.html')

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
                messages.error(request, 'Your account is inactive.')
        else:
            messages.error(request, 'Invalid login details supplied.')
        return render(request, 'greatkart/signin.html')


# class logout(View):
#     @login_required(login_url='login')
#     def post(self,request):
#         logout(request)
#         return redirect('login')

class adminDashboard(View):
    def get(self,request):
        return render(request, 'evara-backend/index.html')
    
class categoryView(View):
    def get(self,request):
        category_set = Category.objects.all()
        context = {
            'category_set': category_set
        }
        return render(request, 'evara-backend/page-categories.html', context)
    
    def post(self,request):
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

class order_list(View):
    def get(self, request):
        order_list = Order.objects.all().order_by('-order_date')
        orders=[]
        for order in order_list:
            total_pr = order.calculate_total_price()
            orders.append((order, total_pr))
            print(total_pr)
        for i in orders:
            print(i)
        context = {
            'order_list': order_list,
            'orders':orders,
        }
        return render(request, 'evara-backend/page-orders-1.html', context)

class product_list(View):
    def get(self,request):
        productlist = Product.objects.all()
  
        context={
            'productlist': productlist
        
        }
        return render(request,'evara-backend/page-products-list.html', context)

class add_product(View):
    def get(self,request):
        category_list = Category.objects.all()
        
        context = {
            'category_list': category_list
        }
        return render(request,'evara-backend/page-form-product-1.html', context)
    
    def post(self,request):
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
    
    
class product_detail(View):
    def get(self,request):
        return render(request,'evara-backend/product-detail.html')

class customers_list(View):
    def get(self,request):
        user_set = Account.objects.all().order_by('-date_joined')
        return render(request,'evara-backend/page-customers-list.html',{'userlist':user_set})

class user_block(View):
    def get(self, request, user_id):
        user = Account.objects.get(pk=user_id)
        user.is_active=False
        user.save()
        print(user.is_active)
        return redirect('customers_list')
    
class user_unblock(View):
    def get(self, request, user_id):
        user = Account.objects.get(pk=user_id)
        user.is_active=True
        user.save()
        print(user.is_active)
        return redirect('customers_list')