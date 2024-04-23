from django.shortcuts import get_object_or_404, render
from .models import Product, ProductImage, ProductVariation
from accounts.models import Account
from category.models import Category
from django.db.models import Q
# # Create your views here.

# def store(request):
#     product = Product.objects.all().filter(is_available=True)
#     product_count = product.count()

#     context = {
#         'products':product,
#         'products_count':product_count
#     }
#     return render(request,'',context)

from django.views import View

class store(View):
    def get(self,request):
        category = None
        products = None 
        # user_id = request.session['user_id']
        print(request.user)
        user = Account.objects.get(email=request.user)
  
        username = user.username
        category_filter = Category.objects.all()
         
        selected_categories = request.GET.getlist('category_filter')
           
        print(selected_categories)
        # print(category_url)
        
        if len(selected_categories) != 0:
            products = Product.objects.filter(category__slug__in=selected_categories, is_available=True)
            prod_count = products.count()

        else:
            products = Product.objects.all().filter(is_available=True)
            prod_count = products.count()
            category = Category.objects.all()

        if 'keyword' in request.GET:
            keyword = request.GET.get('keyword')
            products = Product.objects.order_by('modified_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains = keyword))
            prod_count = products.count(  )

        max_price = request.GET.get('price_filter')
        if max_price is not None:
            products = products.filter( promotion_price__lte=max_price)
            prod_count=products.count()

        context = {
            'products': products,
            'prod_count': prod_count,
            'category': category,
            'user_name': username,
            'category_filter':category_filter,
            # 'category_url':category_url,
            # 'max_price':max_price,
            
        }
        return render(request, 'reid/shop.html', context)

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
        return render(request,'reid/product-details.html',context)
    

class search(View):
    def get(self,request):
        user_id = request.session['user_id']
        user = Account.objects.get(pk=user_id)
        username = user.username
        
        
        if 'keyword' in request.GET:
            keyword = request.GET.get('keyword')
            products = Product.objects.order_by('modified_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains = keyword))
            product_count = products.count(  )
        context={
            'user_name': username,
            'products': products,
            'prod_count':product_count
        }
        return render(request, 'reid/shop.html', context)
    
class sort(View):
    def get(self,request,*args, **kwargs):
        user_id = request.session['user_id']
        user = Account.objects.get(pk=user_id)
        username = user.username
        category_filter = Category.objects.all()

        # category_filter = category_url .split(',') if category_url else []
        # print(category_filter)

        # if category_filter is not None:
        #     products = Product.objects.filter(category__slug__in=category_filter, is_available=True)
        #     prod_count = products.count()

        # else:
        #     products = Product.objects.all().filter(is_available=True)
        #     prod_count = products.count()
        #     category = Category.objects.all()
        
        # if max_price is not None:
        #     products = products.filter( promotion_price__lte=max_price)
        #     prod_count=products.count()
        

        sort_value = request.GET.get('orderby')
        # sort_value = kwargs.get('value')
        if sort_value == 'new':
            products = Product.objects.all().order_by('-modified_date')
        elif sort_value == 'popularity':
            products = Product.objects.all().order_by('popularity')
        elif sort_value == 'LowtoHigh':
            products = Product.objects.all().order_by('promotion_price')
        elif sort_value == 'HightoLow':
            products = Product.objects.all().order_by('-promotion_price')
        elif sort_value == 'rating':
            products = Product.objects.all().order_by('average_rating')
        elif sort_value == 'a-z':
            products = Product.objects.all().order_by('product_name')
        elif sort_value == 'z-a':
            products = Product.objects.all().order_by('-product_name')
        context = {
            'user_name': username,
            'products': products,
            'prod_count': products.count(),
            'category_filter':category_filter,
        }
        return render(request,'reid/shop.html',context)