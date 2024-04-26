from django.shortcuts import get_object_or_404, render, redirect
from .models import Product, ProductImage, ProductVariation
from accounts.models import Account
from category.models import Category
from django.db.models import Q
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
# # Create your views here.

from django.views import View

class store(View):
    def get(self,request):
        category = None
        products = None 
        print(request.user)
        user_id = request.session.get('user_id')  # Use get method to avoid KeyError
        user = None  # Initialize user to None

        if user_id is not None:  # Check if user_id exists
            user = get_object_or_404(Account, pk=user_id)
        category_filter = Category.objects.all()
         
        selected_categories = request.GET.getlist('category_filter')
           
        print(selected_categories)
        # print(category_url)
        
        if len(selected_categories) != 0:
            products = Product.objects.filter(category__slug__in=selected_categories, is_available=True)
            paginator = Paginator(products, 6)
            page = request.GET.get('page')
            paged_products = paginator.get_page(page)
            prod_count = products.count()

        else:
            products = Product.objects.all().filter(is_available=True)
            prod_count = products.count()
            paginator = Paginator(products, 6)
            page = request.GET.get('page')
            paged_products = paginator.get_page(page)
            category = Category.objects.all()

        if 'keyword' in request.GET:
            keyword = request.GET.get('keyword')
            products = Product.objects.filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword),is_available=True).order_by('modified_date')
            paginator = Paginator(products, 6)
            page = request.GET.get('page')
            paged_products = paginator.get_page(page)
            prod_count = products.count(  )

        max_price = request.GET.get('price_filter')
        if max_price is not None:
            products = products.filter( promotion_price__lte=max_price,  is_available=True)
            paginator = Paginator(products, 6)
            page = request.GET.get('page')
            paged_products = paginator.get_page(page)
            prod_count=products.count()

        context = {
            'products': paged_products,
            'prod_count': prod_count,
            'category': category,
            'user_id':user_id,
            'user': user,
            'category_filter':category_filter,
            
        }
        return render(request, 'reid/shop.html', context)

class product_detail(View):   
    def get(self,request, category_slug, product_slug, size):
        print(size)
        user_id = request.session.get('user_id')  # Use get method to avoid KeyError
        user = None  # Initialize user to None

        if user_id is not None:  # Check if user_id exists
            user = get_object_or_404(Account, pk=user_id)

        print(user_id)
        print(user)
        
        try:
            single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
            images = ProductImage.objects.filter(product=single_product)
            print('before')
            try:
                variant = ProductVariation.objects.get(product=single_product, size=size)
            except:
                variant = None
            print('after')
            print(variant)
        except Exception as e:
            return redirect('store')
        context = {
            'single_product': single_product,
            'images':images,
            'user_id':user_id,
            'user': user, 
            'variant':variant,
            'category_slug':category_slug,
            'product_slug':product_slug
        }
        return render(request,'reid/product-details.html',context)
    
class sort(View):
    def get(self,request,*args, **kwargs):
        user_id = request.session.get('user_id')  # Use get method to avoid KeyError
        user = None  # Initialize user to None

        if user_id is not None:  # Check if user_id exists
            user = get_object_or_404(Account, pk=user_id)
        category_filter = Category.objects.all()

        sort_value = request.GET.get('orderby')
        if sort_value == 'new':
            products = Product.objects.all().order_by('-modified_date').filter(is_available=True)
        elif sort_value == 'popularity':
            products = Product.objects.all().order_by('popularity').filter(is_available=True)
        elif sort_value == 'LowtoHigh':
            products = Product.objects.all().order_by('promotion_price').filter(is_available=True)
        elif sort_value == 'HightoLow':
            products = Product.objects.all().order_by('-promotion_price').filter(is_available=True)
        elif sort_value == 'rating':
            products = Product.objects.all().order_by('average_rating').filter(is_available=True)
        elif sort_value == 'a-z':
            products = Product.objects.all().order_by('product_name').filter(is_available=True)
        elif sort_value == 'z-a':
            products = Product.objects.all().order_by('-product_name').filter(is_available=True)
        context = {
            'user_id':user_id,
            'user': user,
            'products': products,
            'prod_count': products.count(),
            'category_filter':category_filter,
        }
        return render(request,'reid/shop.html',context)