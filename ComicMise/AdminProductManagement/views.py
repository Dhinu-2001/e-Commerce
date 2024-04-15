from django.shortcuts import render
from django.views import View
from django.http import JsonResponse

# Model importing
from store.models import Product
# Create your views here.

class product_listing(View):
    def post(self, request, product_id):
        try:
            print('working')
            product = Product.objects.get(id = product_id)
            if product.is_available:
                product.is_available = False
                list_status = 'Unlisted'
            else:
                product.is_available = True
                list_status = 'Listed'
            product.save()
            print(product.is_available)
            print(list_status)
            return JsonResponse({'success': True,'list_status': list_status})
        except Product.DoesNotExist:
            return JsonResponse({'error':'Product not found'}, status=404)