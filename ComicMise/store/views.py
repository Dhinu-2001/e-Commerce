from django.shortcuts import render
from .models import Product
from accounts.models import Account
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
        return render(request, 'greatkart/store.html', context)
    
class sort(View):
    def get(self,request,*args, **kwargs):
        user_id = request.session['user_id']
        user = Account.objects.get(pk=user_id)
        username = user.username

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
            'prod_count': products.count()
        }
        return render(request,'reid/shop.html',context)