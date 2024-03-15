from django.shortcuts import render
from .models import Product
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
        if 'keyword' in request.GET:
            keyword = request.GET.get('keyword')
            products = Product.objects.order_by('modified_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains = keyword))
            product_count = products.count(  )
        context={
            'products': products,
            'prod_count':product_count
        }
        return render(request, 'greatkart/store.html', context)
    
class sort(View):
    def get(self,request,*args, **kwargs):
        sort_value = kwargs.get('value')
        if sort_value == 'new':
            products = Product.objects.all().order_by('-modified_date')
        elif sort_value == 'popularity':
            products = Product.objects.all().order_by('popularity')
        elif sort_value == 'LowtoHigh':
            products = Product.objects.all().order_by('price')
        elif sort_value == 'HightoLow':
            products = Product.objects.all().order_by('-price')
        elif sort_value == 'rating':
            products = Product.objects.all().order_by('average_rating')
        elif sort_value == 'a-z':
            products = Product.objects.all().order_by('product_name')
        elif sort_value == 'z-a':
            products = Product.objects.all().order_by('-product_name')
        context = {
            'products': products,
            'prod_count': products.count()
        }
        return render(request,'greatkart/store.html',context)