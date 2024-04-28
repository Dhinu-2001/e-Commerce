from django.shortcuts import get_object_or_404, render

# Create your views here.
from django.shortcuts import render, redirect
from django.views import View
from accounts.models import Account
from .models import User_wishlist
from store.models import Product, ProductVariation
from cart.models import Cart, CartItem
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
# Create your views here.

@method_decorator(login_required(login_url="login"), name="dispatch")
class wishlist(View):
    def get(self, request):
        user_id = request.session.get('user_id')  # Use get method to avoid KeyError
        user = None  # Initialize user to None

        if user_id is not None:  # Check if user_id exists
            user = get_object_or_404(Account, pk=user_id)

        try:
            wishlist = User_wishlist.objects.get(user = user)
        except User_wishlist.DoesNotExist:
            wishlist = User_wishlist.objects.create(user = user)
        wishlist.save()
        wishlist_products=[]
        products = wishlist.products.all()
        for product in products:
            prod_varis = ProductVariation.objects.filter(product=product)
            flag = 0
            for i in prod_varis:
                if i.stock != 0:
                    flag = 1
            if flag == 0:
                stock_status = 'Out of stock'
            else:
                stock_status = 'In stock'
        
            wishlist_products.append((stock_status,wishlist,product))
            
        
        context={
            'user_id':user_id,
            'user': user,
            'wishlist_products':wishlist_products,
        }
        return render(request,'reid/wishlist.html',context)

@method_decorator(login_required(login_url="login"), name="dispatch")
class add_wishlist(View):
    def get(self, request, product_id):
        user_id = request.session.get('user_id')  # Use get method to avoid KeyError
        user = None  # Initialize user to None

        if user_id is not None:  # Check if user_id exists
            user = get_object_or_404(Account, pk=user_id)

        product = Product.objects.get(id = product_id)

        try:
            wishlist = User_wishlist.objects.get(user = user)
        except User_wishlist.DoesNotExist:
            wishlist = User_wishlist.objects.create(user = user)
        wishlist.products.add(product)   
        wishlist.save()
        return redirect('wishlist')
    
@method_decorator(login_required(login_url="login"), name="dispatch")
class remove_wishlist(View):
    def get(self, request, product_id):
        user_id = request.session.get('user_id')  # Use get method to avoid KeyError
        user = None  # Initialize user to None

        if user_id is not None:  # Check if user_id exists
            user = get_object_or_404(Account, pk=user_id)
        wishlist = User_wishlist.objects.get(user = user)
        product = Product.objects.get(id = product_id)

        wishlist.products.remove(product)
        #wishlist_prods = wishlist.products.all()
        # wishlist_prod = wishlist_prods.objects.get(Product = product)
        # for wishlist_prod in wishlist_prods:
        #     if wishlist_prod.id == product_id:
        #         wishlist_prod.delete() 
        return redirect('wishlist')
    
def cart_id(request):
    cart_id= request.session.session_key
    if not cart_id:
        cart_id = request.session.create()
    return cart_id

@method_decorator(login_required(login_url="login"), name="dispatch")
class wishlist_add_cart(View):
    def get(self,request,product_id):
        product = Product.objects.get(pk = product_id)
        size = 'small'
        variant = ProductVariation.objects.get(product=product, size=size)
        try:
            cart = Cart.objects.get(cart_id = cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id = cart_id(request))
        cart.save()
        print(product,variant,cart)

        try:
            cart_item = CartItem.objects.get(
                product =product,
                variations = variant,
                cart = cart
                )
            cart_item.quantity += 1
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product = product,
                cart = cart,
                quantity = 1
            )
            cart_item.variations.add(variant)
            cart_item.save()
        
        user_id = request.session.get('user_id')
        user = Account.objects.get(id = user_id)
        wishlist =User_wishlist.objects.get(user = user)
        wish_product = Product.objects.get(id = product_id )

        wishlist.products.remove(wish_product)

        return redirect('cart')
    