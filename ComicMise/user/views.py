import calendar
import datetime
from django.db.models import Sum, Count, Prefetch
from django.shortcuts import render,redirect, get_object_or_404
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



class home(View):
    def get(self,request):
        #user_id = Account.objects.get(pk=pk)
        products = Product.objects.all().filter(is_available=True)
        user_id = request.session.get('user_id')  # Use get method to avoid KeyError
        user = None  # Initialize user to None

        if user_id is not None:  # Check if user_id exists
            user = get_object_or_404(Account, pk=user_id)

        category_filter = Category.objects.all()

        context = {
            'products': products,
            'user_id':user_id,
            'user': user,
            'category_filter':category_filter
        }
        return render(request, 'reid/index.html', context)


# class logout(View):
#     @login_required(login_url='login')
#     def post(self,request):
#         logout(request)
#         return redirect('login')



class adminDashboard(View):
    def monthly_earnings(self):
        current_year = timezone.now().year
        current_month = timezone.now().month

        # Get the number of days in the current month
        _, num_days = calendar.monthrange(current_year, current_month)

        # Calculate the start and end dates for the current month
        start_date = timezone.datetime(current_year, current_month, 1)
        end_date = timezone.datetime(current_year, current_month, num_days, 23, 59, 59)

        # Calculate the total earnings for the current month
        monthly_earnings = (
            Order.objects.filter(order_date__range=(start_date, end_date)).aggregate(
                total_earnings=Sum("total_price")
            )["total_earnings"]
            or 0
        )
        return monthly_earnings
    
#============= Best selling PRODUCT ===================================================

    def get_most_ordered_products_with_count(self):
        # Aggregate the number of orders for each product
        ordered_products = OrderItem.objects.values('product').annotate(total_orders=Count('product'))

        # Order the products by total order count in descending order and retrieve the top 10
        most_ordered_products = ordered_products.order_by('-total_orders')[:10]

        # Create a list to store tuples of (Product object, total order count)
        products_with_count = []

        # Retrieve the Product objects and total order count for the most ordered products
        for product_data in most_ordered_products:
            product_id = product_data['product']
            total_orders = product_data['total_orders']
            product_obj = Product.objects.get(pk=product_id)
            products_with_count.append((product_obj, total_orders))

        return products_with_count
#========================================================================================
#=================== Best Selling CATEGORY ==============================================


    def get_most_ordered_categories_with_count(self):
        # Aggregate the number of orders for each category
        ordered_categories = OrderItem.objects.values('product__category').annotate(total_orders=Count('product__category'))

        # Order the categories by total order count in descending order and retrieve the top 10
        most_ordered_categories = ordered_categories.order_by('-total_orders')[:10]

        # Create a list to store tuples of (Category object, total order count)
        categories_with_count = []

        # Retrieve the Category objects and total order count for the most ordered categories
        for category_data in most_ordered_categories:
            category_id = category_data['product__category']
            total_orders = category_data['total_orders']
            category_obj = Category.objects.get(pk=category_id)
            categories_with_count.append((category_obj, total_orders))

        return categories_with_count


#==========================================================================================
    def get(self,request):
        user_id = request.session.get('user_id')
        user = Account.objects.get(id = user_id)
        try:
            if not user.is_admin:
                return redirect("login")
        except :
            return redirect("login")
        orders = Order.objects.filter(order_status="Delivered")
        order_count = orders.count()

        revenue = (
            orders.aggregate(total_revenue=Sum("total_price"))["total_revenue"] or 0
        )

        chart_month = [0] * 12
        new_users = [0] * 12
        orders_count = [0] * 12

        for order in orders:
            month = order.order_date.month - 1
            chart_month[month] += order.total_price
            orders_count[month] += 1
        # print(month, chart_month, orders_count)

        for user in Account.objects.all():
            month = user.date_joined.month - 1
            new_users[month] += 1

        all_orders = Order.objects.all().order_by("-order_date")[:10]

        date = request.GET.get("date")
        # order_filter = request.GET.get("order_filter")

        # if order_filter and order_filter != "All":
        #     all_orders = all_orders.filter(payment_status=order_filter)

        # if date:
        #     date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        #     all_orders = all_orders.filter(order_date__date=date_obj)

        products_count = Product.objects.all().count()
        categories_count = (
            Product.objects.values("category").distinct().count()
        )

        monthly_earning = self.monthly_earnings()

        most_ordered_products_with_count = self.get_most_ordered_products_with_count()
        most_ordered_categories_with_count = self.get_most_ordered_categories_with_count()
       


        context = {
           "revenue": revenue,
           "order_count": order_count,
           "products_count": products_count,
           "categories_count": categories_count,
           "monthly_earning": monthly_earning,
           "month": chart_month,
           "new_users": new_users,
           "orders_count": orders_count,
           "users": Account.objects.filter(is_admin=False).order_by("-date_joined")[:5],
           "most_ordered_products_with_count":most_ordered_products_with_count,
           "most_ordered_categories_with_count":most_ordered_categories_with_count,
        #    "orders": all_orders,
        #    "date": date,
        #    "order_filter": order_filter,
           
           
           
        }

        return render(request, 'evara-backend/index.html',context)
    
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
        payment_status = order.payment_method
        payment_method_choice = order.PAYMENT_METHOD_CHOICES
        pay_method = [choice[1] for choice in payment_method_choice if choice[0] == payment_status ]
        order_status_choices = Order.ORDER_STATUS_CHOICES
        
        print(order.payment_status)
        print(order.total_price)
        context = {
            'order':order,
            'order_items':order_items,
            'pay_method':pay_method[0],
            'order_status_choices':order_status_choices,
            'order_cancel_status':order.canceled,
        }

        return render(request, 'evara-backend/page-orders-detail.html', context)
    
class order_status_change(View):
    def post(self, request, order_id):
        order = Order.objects.get(id = order_id)
        order_status = request.POST.get('order_status')
        if order_status == 'Delivered':
            order.payment_status = 'SUCCESS'
        order.order_status=order_status
        print(order_status)
        order.save()
        return redirect('order_detail', order_id=order_id)
    
class admin_cancel_order(View):
    def get(self, request, order_id):
        user = Account.objects.get(email=request.user)
        order = Order.objects.get(id = order_id)
        if order.canceled is False:
            order.canceled = True
            if order.payment_status == 'Success':
                wallet = wallet.objects.get(user=user)
                wallet.amount += order.total_price
                wallet.save()
                  
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
        productlist = Product.objects.all().order_by('-modified_date')
  
        context={
            'productlist': productlist
        
        }
        return render(request,'evara-backend/page-products-list.html', context)

class add_product(View):
    def get(self,request):
        category_list = Category.objects.all()
        
        context = {
            'category_list': category_list,
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
                
                for img in prod_images:
                    ProductImage.objects.create(product=product_inst, image=img)    
                return redirect('product_list')
            else:
                messages.error(request,'Please upload 3 images.')
                return redirect('add_product')
    
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