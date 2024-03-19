from django.shortcuts import redirect, render
from django.views import View
from . models import Cart, CartItem
from store.models import Product, ProductVariation
from accounts.models import Account

# Create your views here.
def cart_id(request):
    cart_id= request.session.session_key
    if not cart_id:
        cart_id = request.session.create()
    return cart_id

class add_cart(View):
    def get(self,request,product, variant):
        print(product,variant)
        product = Product.objects.get(pk = product)
        variant = ProductVariation.objects.get(pk = variant)
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

        return redirect('cart')
    
class remove_cart(View):
    def get(self, request, product, variant):
        product = Product.objects.get(pk = product)
        variant = ProductVariation.objects.get(pk = variant)
        cart = Cart.objects.get(cart_id = cart_id(request))
        cart_item = CartItem.objects.get(cart = cart, product = product, variations = variant)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
        return redirect('cart')
    
class remove_cart_item(View):
    def get(self, request, product, variant):
        product = Product.objects.get(pk = product)
        variant = ProductVariation.objects.get(pk = variant)
        cart = Cart.objects.get(cart_id = cart_id(request))
        cart_item = CartItem.objects.get(cart = cart, product = product, variations = variant)
        cart_item.delete()
        return redirect('cart')


class cart(View):
    def get(self,request, total=0, quantity=0, cart_items=None):
        try:
            cart = Cart.objects.get(cart_id=cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart, is_active=True)
            for cart_item in cart_items:
                total += (cart_item.product.price * cart_item.quantity)
                quantity += cart_item.quantity
                variants = cart_item.variations.all()
                for variant in variants:
                    variant=variant.id
        except Cart.DoesNotExist:
            pass
        
        context = {
            'total': total,
            'quantity':quantity,
            'cart_items': cart_items,
            'variant': variant,
        }
        
        return render(request, 'evara-frontend/shop-cart.html',context)