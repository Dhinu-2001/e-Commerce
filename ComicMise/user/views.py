from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login as auth_login
from django.views import View
from django.utils.decorators import method_decorator
#Import Models
from accounts.models import Account
from category.models import Category
from store.models import Product, ProductImage, ProductVariation, Variants
from cart.models import Order, OrderItem
from wallet.models import Wallet
from django.utils import timezone
from django.middleware.csrf import get_token

from django.http import HttpResponse
from django.contrib import messages
# Create your views here.

class Login(View):
    def get(self,request):
        
        return render(request,'reid/login.html')
    
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not email or not password:
            messages.error(request, 'Enter email and password')
            return render(request, 'reid/login.html')

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
        return render(request, 'reid/login.html')


# class logout(View):
#     @login_required(login_url='login')
#     def post(self,request):
#         logout(request)
#         return redirect('login')

class adminDashboard(View):
    def get(self,request):
        user_id = request.session.get('user_id')
        print(user_id)
        user = Account.objects.get(id = user_id)
        try:
            if not user.is_admin:
                return redirect("login")
        except :
            return redirect("login")
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
    
class order_detail(View):
    def get(self, request, order_id):
        order = Order.objects.get(id = order_id)
        order_items = OrderItem.objects.filter(order = order)

        order_status_choices = Order.ORDER_STATUS_CHOICES
        
        context = {
            'order':order,
            'order_items':order_items,
            'order_status_choices':order_status_choices,
            'order_cancel_status':order.canceled,
        }

        return render(request, 'evara-backend/page-orders-detail.html', context)
    
class order_status_change(View):
    def post(self, request, order_id):
        order = Order.objects.get(id = order_id)
        order_status = request.POST.get('order_status')
        order.order_status=order_status
        print(order_status)
        order.save()
        return redirect('order_detail', order_id=order_id)
    
class admin_cancel_order(View):
    def get(self, request, order_id):
        order = Order.objects.get(id = order_id)
        if order.canceled is False:
            order.canceled = True
        else:
            order.canceled = False            
        order.save()
        return redirect('order_detail', order_id=order_id)
    
class admin_return_decision(View):
    def get(self, request, order_id, dec):
        order =Order.objects.get(id = order_id)
        return_choices = Order.RETURN_STATUS_CHOICES
        if dec == 'accepted':
            order.is_returned=return_choices[2][0]
            user_id = request.session.get('user_id')
            user = Account.objects.get(id = user_id)
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


        elif dec == 'declined':
            order.is_returned=return_choices[0][0]
        
        order.save()
        print(dec, return_choices[2][0], return_choices[0][0])
        return redirect('order_detail', order_id=order_id)


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
            prom_price       = request.POST['promotion_price']
            reg_price       = request.POST['regular_price']
            prod_cat_slug    = request.POST.get('product_category')
            # prod_size        = request.POST.get('product_size')
            # prod_stock       = request.POST.get('product_stock')
            prod_images      = [request.FILES.get('image1'), request.FILES.get('image2'), request.FILES.get('image3')]
  
        
            #checking.....
            if not prod_name or not prod_description or not prom_price  or not prod_cat_slug :
                messages.error(request,'Enter the required fields')
                return redirect('add_product')
        
            #getting category-Instanse using primary key
            category_inst=Category.objects.get(slug=prod_cat_slug)
        

            if len(prod_images) == 3 and all(prod_images):
                fd = Product(product_name=prod_name, description = prod_description, promotion_price= prom_price,regular_price = reg_price, category=category_inst) 
                fd.save()

                #getting Instance
                product_inst = Product.objects.get(product_name=prod_name)
                # size_inst    = SizeVariant.objects.get(size=prod_size)

                # variation = ProductVariation.objects.filter(product=product_inst, size=prod_size)
                
                # if variation:
                # If the variation exists, update the stock_quantity
                #     variation.stock += prod_stock
                #     variation.save()
                # else:
                # If the variation doesn't exist, create a new entry
                    # ProductVariation.objects.create(product=product_inst, size=prod_size, stock=prod_stock)
                    # variation.save()
                for img in prod_images:
                    ProductImage.objects.create(product=product_inst, image=img)    
                return redirect('product_list')
            else:
                messages.error(request,'Please upload 3 images.')
                return redirect('add_product')
                        
            # return redirect('product_detail', product_id=product_id)
                
        # category_list = Category.objects.all()
        
        # context = {
        #     'category_list': category_list
            
        # }
        # return render(request,'evara-backend/page-form-product-1.html', context)
    
    
class product_detail(View):
    def get(self,request, product_id):
        product = Product.objects.get(id = product_id)
        images = ProductImage.objects.filter(product=product)
        try:
            table_variations = ProductVariation.objects.filter(product = product_id)
        except ProductVariation.DoesNotExist:
            table_variations = None
        context = {
            'product':product,
            'images':images,
            'table_variations':table_variations,
            'csrf_token': get_token(request)
        }
        return render(request,'evara-backend/product-detail.html', context)
    
class stock_update(View):
    def get(self, request, product_id):
        product = Product.objects.get(id = product_id)
        try:
            table_variations = ProductVariation.objects.filter(product = product_id)
        except ProductVariation.DoesNotExist:
            table_variations = None
        drop_down_variations = Variants.objects.all()
        context ={
            'product': product,
            'drop_down_variations':drop_down_variations,
            'table_variations':table_variations,
        }
        return render(request, 'evara-backend/stock_update.html',context)
    def post(self, request, product_id):
        product = Product.objects.get(id = product_id)
        product_variant = request.POST.get('product_size')
        product_stock = int(request.POST.get('product_stock'))
        try:
            variant_checking = ProductVariation.objects.get(product = product, size = product_variant)
            variant_checking.stock += product_stock
            variant_checking.save()
        except ProductVariation.DoesNotExist:
            Prod_Vari_stock = ProductVariation(product = product, size = product_variant, stock = product_stock)
            Prod_Vari_stock.save()
        return redirect('stock_update', product_id=product_id)

class add_new_variant(View):
    def post(self, request, product_id):
        new_variant = request.POST.get('new_variant')
        try:
            variant_checking = Variants.objects.get(variant=new_variant)
            messages.error(request,'Variant exists')
            return redirect('stock_update', product_id=product_id)
        except Variants.DoesNotExist:
            variant = Variants(variant = new_variant)
            variant.save()
            
        return redirect('stock_update', product_id=product_id)

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
    
class sales_report(View):
    def get(self, request):
        sales_from = request.GET.get('sales_from')
        sales_to = request.GET.get('sales_to')
        if sales_from and sales_to:
            
            start_date = sales_from
            end_date = sales_to
            orders = Order.objects.filter(order_date__range=(start_date, end_date)).filter(order_status = 'Delivered').order_by('-order_date')
            overall_sale_count = Order.objects.filter(order_date__range=(start_date, end_date)).filter(order_status = 'Delivered').count()
            overall_order_amount = 0
            overall_order_discount = 0
            for order in orders:
                overall_order_amount += order.total_price 
                overall_order_discount += order.price_discounted
        else:
            orders = Order.objects.filter(order_status = 'Delivered').order_by('-order_date')
            overall_sale_count = Order.objects.filter(order_status = 'Delivered').count()
            overall_order_amount = 0
            overall_order_discount = 0
            for order in orders:
                overall_order_amount += order.total_price 
                overall_order_discount += order.price_discounted
        

        # trans=[]
        # total_price_for_each_order=[]
        # for order in orders:
        #     order_items = OrderItem.objects.filter(order = order)
        #     total_price=0
        #     for order_item in order_items:
        #         total_price += order_item.price
        #     total_price_for_each_order.append(total_price)

        
        context={
            'orders':orders,
            'overall_sale_count':overall_sale_count,
            'overall_order_amount':overall_order_amount,
            'overall_order_discount':overall_order_discount,
        }
        return render(request,'evara-backend/sales_report.html', context)