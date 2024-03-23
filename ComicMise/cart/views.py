from django.shortcuts import redirect, render
from django.views import View
from . models import Cart, CartItem, Order, OrderItem
from store.models import Product, ProductVariation
from accounts.models import Account, Address
from django.contrib import messages
from django.http import HttpResponse

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
        print(variant)
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
            cart_items_variations = []
            for cart_item in cart_items:
                total += (cart_item.product.price * cart_item.quantity)
                quantity += cart_item.quantity
                variations = cart_item.variations.all()
                for variation in variations:
                    print(variation.size)
                    cart_items_variations.append((cart_item, variation))
                        
               
        except Cart.DoesNotExist:
            pass
        
        context = {
            'total': total,
            'quantity':quantity,
            'cart_items_variations': cart_items_variations,
        }
        
        return render(request, 'evara-frontend/shop-cart.html',context)
    
class place_order(View):
    def get(self, request, total=0, quantity=0, cart_items=None):
        user_id = request.session['user_id']
        user = Account.objects.get(pk=user_id)
        username = user.username
        addresses = user.addresses.all()
        try:
            cart = Cart.objects.get(cart_id=cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart, is_active=True)
            cart_items_variations = []
            for cart_item in cart_items:
                total += (cart_item.product.price * cart_item.quantity)
                quantity += cart_item.quantity
                variations = cart_item.variations.all()
                for variation in variations:
                    print(variation.size)
                    cart_items_variations.append((cart_item, variation))
                        
               
        except Cart.DoesNotExist:
            pass
        
        context = {
            'total': total,
            'quantity':quantity,
            'cart':cart.id,
            'cart_items_variations': cart_items_variations,
            'user_name': username,
            'addresses': addresses,
        }
        return render(request, 'evara-frontend/shop-checkout.html',context)
    
class order_success(View):
    def post(self, request, cart, user_name):
        
        deli_address_id = request.POST.get('delivery_address')

        if deli_address_id == 'new address':
            address_title    = request.POST['address_title']
            name             = request.POST['name']
            ph_number        = request.POST['ph_number']
            pincode          = request.POST['pincode']
            locality         = request.POST['locality']
            address          = request.POST['address']
            city             = request.POST['city']
            state            = request.POST['state']
            landmark         = request.POST['landmark']
            alt_phone_number = request.POST['alt_phone_number']


            if not address_title or not ph_number or not pincode or not address or not locality or not city or not state or not name:
                messages.error(request,'Enter the required fields')
                return redirect('place_order' )

            fd = Address(address_title=address_title, name=name, ph_number=ph_number, pincode=pincode, locality=locality, address=address, city=city, state=state, landmark=landmark, alt_phone_number=alt_phone_number)
            fd.save()

            user_id = request.session['user_id']
            user = Account.objects.get(pk=user_id)
            user.addresses.add(fd)

            address = fd
        else:
            address =Address.objects.get(id=deli_address_id) 
        user_id = request.session['user_id']
        user = Account.objects.get(pk=user_id)
        payment_method = request.POST.get('payment_option')

        order_submit = Order(user=user, payment_method=payment_method, shipping_address=address )
        order_submit.save()

        cart_items = CartItem.objects.filter(cart = cart, is_active=True)
        for cart_item in cart_items:
            product = cart_item.product
            variations = cart_item.variations.all()
            print(variations)
            quantity = cart_item.quantity
            price = cart_item.sub_total()
            
            order_item = OrderItem(
                order = order_submit,
                product = product,
                quantity = quantity,
                price = price,
            )
            
            #  order_item.variations.add(variation)
            order_item.save()
            order_item.variations.set(cart_item.variations.all())

        order_items = Order.objects.

        context={
            'order_no': order_submit.id,
            'order_date': order_submit.order_date,
            'order_method': order_submit.payment_method,
            'shipping_address': order_submit.shipping_address,
            'item_name':order
        }

        return render(request, 'evara-frontend/order_success.html',context)

