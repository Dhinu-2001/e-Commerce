from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from category.models import Category
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test

# Model importing
from store.models import Product, ProductImage
# Create your views here.

def is_admin(user):
    return user.is_admin

@method_decorator(user_passes_test(is_admin), name='dispatch')
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
    
@method_decorator(user_passes_test(is_admin), name='dispatch')
class edit_product(View):
    def get(self, request, product_id):
        product = Product.objects.get(id = product_id)
        category_list = Category.objects.all()
        context ={
            'product':product,
            'category_list': category_list
        }
        return render(request, 'evara-backend/edit_product.html', context)
    
    def post(self, request, product_id):
        prod_name        = request.POST['product_name']
        prod_description = request.POST['product_description']
        prom_price       = request.POST['promotion_price']
        reg_price        = request.POST['regular_price']
        prod_cat_slug    = request.POST.get('product_category')
        prod_images      = [request.FILES.get('image1'), request.FILES.get('image2'), request.FILES.get('image3')]
        print(prod_images)
        print(all(prod_images))
        category_inst=Category.objects.get(slug=prod_cat_slug)
        # #getting category-Instanse using primary key
        product = Product.objects.get(id = product_id)

        product.product_name = prod_name
        product.description = prod_description
        product.promotion_price = prom_price
        product.regular_price = reg_price
        product.category = category_inst
        product.save()

        if len(prod_images) == 3 and all(prod_images):
            product_inst = Product.objects.get(id=product_id)
            Prod_oldImages = ProductImage.objects.filter(product=product_inst)
            Prod_oldImages.delete()

            for img in prod_images:
                ProductImage.objects.create(product=product_inst, image=img)    
            return redirect('product_detail', product_id=product_id)
        
        else:
            return redirect('product_detail', product_id=product_id)
        
        # else:
        #     messages.error(request,'Please upload 3 images.')
        #     return redirect('edit_product', product_id=product.id)
        