from django.utils import timezone
from django.shortcuts import redirect, render
from django.views import View
from . models import Cart, CartItem, Order, OrderItem
from store.models import Product, ProductVariation
from accounts.models import Account, Address
from django.contrib import messages
from django.http import HttpResponse
import razorpay 
from django.views.decorators.csrf import csrf_exempt
from coupon.models import Coupon

# Create your views here.
def cart_id(request):
    cart_id= request.session.session_key
    if not cart_id:
        cart_id = request.session.create()
    return cart_id

class add_cart(View):
    def get(self,request,product_id):
        print(product_id)
        product = Product.objects.get(pk = product_id)
        size = request.GET.get('size')
        print(size)
        variant = ProductVariation.objects.get(product=product, size=size)
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
    def get(self,request, total_price=0, quantity=0, cart_items=None):

        try:
            user_id = request.session['user_id']
            user = Account.objects.get(pk=user_id)
            
            cart = Cart.objects.get(cart_id=cart_id(request))
            print(cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart, is_active=True)
            cart_items_variations = []
            coupon_list = Coupon.objects.all()
            for cart_item in cart_items:
                total_price += (cart_item.product.price * cart_item.quantity)
                quantity += cart_item.quantity
                variations = cart_item.variations.all()
                for variation in variations:
                    print(variation.size)
                    cart_items_variations.append((cart_item, variation))
            coupon_code = request.POST.get('coupon_code')
            if coupon_code is not None:
                current_time = timezone.now()
                coupon = Coupon.objects.get(code = coupon_code)
                if coupon.valid_to >= current_time and coupon.active is True:
                    discount_rate = (coupon.discount / 100)*total_price
                    total_afer_discount = total_price - discount_rate
                    request.session['discount_total'] = total_afer_discount
                    request.session['coupon_code'] = coupon_code
            coupon_code = request.session.get('coupon_code')
            if coupon_code is not None:
                total_grand = request.session.get('discount_total')
            else:
                total_grand = total_price
               
        except Cart.DoesNotExist:
            pass
        print(cart.id)
        context = {
            'cart_total':total_price,
            'total': total_grand,
            'coupon_list':coupon_list,
            'coupon_code':coupon_code,
            'quantity':quantity,
            'cart_items_variations': cart_items_variations,
            'user_name': user.username,
        }
        
        return render(request, 'reid/cart.html',context)
    
    def post(self,request, total_price=0, quantity=0, cart_items=None):
        try:
            user_id = request.session['user_id']
            user = Account.objects.get(pk=user_id)
            
            cart = Cart.objects.get(cart_id=cart_id(request))
            print('1'+cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart, is_active=True)
            cart_items_variations = []
            coupon_list = Coupon.objects.all()

            for cart_item in cart_items:
                total_price += (cart_item.product.price * cart_item.quantity)
                quantity += cart_item.quantity
                variations = cart_item.variations.all()
                for variation in variations:
                    print(variation.size)
                    cart_items_variations.append((cart_item, variation))
            coupon_code = request.POST.get('coupon_code')
            print(coupon_code)
            if coupon_code is not None:
                current_time = timezone.now()
                coupon = Coupon.objects.get(code = coupon_code)
                if coupon.valid_to >= current_time and coupon.active is True:
                    discount_rate = (coupon.discount / 100)*total_price
                    total_afer_discount = total_price - discount_rate
                    request.session['discount_total'] = total_afer_discount
                    request.session['coupon_code'] = coupon_code
            coupon_code = request.session.get('coupon_code')
            if coupon_code is not None:
                total_grand = request.session.get('discount_total')
            else:
                total_grand = total_price
               
        except Cart.DoesNotExist:
            pass
        
        context = {
            'cart_total':total_price,
            'total': total_grand,
            'coupon_list':coupon_list,
            'coupon_code':coupon_code,
            'quantity':quantity,
            'cart_items_variations': cart_items_variations,
            'user_name': user.username,
        }
        
        return render(request, 'reid/cart.html',context)
    
class place_order(View):
    def get(self, request, total_price=0, quantity=0, cart_items=None):
        user_id = request.session['user_id']
        user = Account.objects.get(pk=user_id)
        username = user.username
        addresses = user.addresses.all()
        try:
            cart = Cart.objects.get(cart_id=cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart, is_active=True)
            cart_items_variations = []
            for cart_item in cart_items:
                total_price += (cart_item.product.price * cart_item.quantity)
                quantity += cart_item.quantity
                variations = cart_item.variations.all()
                for variation in variations:
                    print(variation.size)
                    cart_items_variations.append((cart_item, variation))
            
            coupon_code = request.session.get('coupon_code')
            if coupon_code is not None:
                total_grand = request.session.get('discount_total')
            else:
                total_grand = total_price
               
        except Cart.DoesNotExist:
            pass
        
        context = {
            'cart_total':total_price,
            'total': total_grand,
            'quantity':quantity,
            'cart':cart.id,
            'cart_items_variations': cart_items_variations,
            'user_name': username,
            'addresses': addresses,
            'coupon_code':coupon_code,
        }
        return render(request, 'evara-frontend/shop-checkout.html',context)


class order_success(View):
    @csrf_exempt
    def post(self, request, cart, user_name):
        
        payment_method = request.POST.get('payment_option')
        print('payment_method')
        # amount = 50000
            # client = razorpay.Client(
            #     auth=("rzp_test_oRlyX5LhXmmXeJ", "6zxeEQafauF3o4awwAkWYat1"))
            # payment = client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture': '1'})

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

#-------------------------------------------------Order database insertion---------------------------------------------------
        
        order_submit = Order(user=user, payment_method=payment_method, shipping_address=address )
        order_submit.save()
        
        total = 0
        cart_items = CartItem.objects.filter(cart = cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            product = cart_item.product
            variations = cart_item.variations.all()
            print(variations)
            quantity = cart_item.quantity
            price = cart_item.sub_total()
    #---------------------------------------- adding each cart item to order item--------------------------------------------------
            order_item = OrderItem(
                order = order_submit,
                product = product,
                quantity = quantity,
                price = price,
            )
    #----------------------------------------updating stock on the base of variations & deleting the cart item.---------------------
            order_item.save()
            order_item.variations.set(cart_item.variations.all())
            print(order_item, order_item.variations.all())
            for i in order_item.variations.all():
                i.stock -= order_item.quantity
                print(i.stock, order_item.quantity)
                i.save()
            cart_item.delete( )   
        order_i = Order.objects.get(id = order_submit.id)
#------------------------------------------------------------Total amount saving in database--------------------------------  
        coupon_code = request.session.get('coupon_code')
        delete_coupon = request.session.pop('coupon_code', None)
        if coupon_code is not None:
            order_i.total_price = request.session.get('discount_total')
        else:
            order_i.total_price = total
        
        order_i.save()
       #total_price = order_submit.calculate_total_price()
        order_items = OrderItem.objects.filter(order = order_submit)
        order_items_variations=[]
        for order_item in order_items:
            variations = order_item.variations.all()
            for variation in variations:
                order_items_variations.append((order_item, variation))
        
        if payment_method == 'RAZORPAY':
            return redirect('razorpay_name',order_id = order_submit.id)
        

        context={
            'coupon_code':coupon_code,
            'order_no': order_submit.id,
            'order_date': order_submit.order_date,
            'order_method': order_submit.payment_method,
            'shipping_address': order_submit.shipping_address,
            'order_items_variations':order_items_variations,
            'total':total,
            'user_name':user.username  
        }
        return render(request, 'evara-frontend/order_success.html',context)
        
        # elif payment_method == 'RAZORPAY':
        #     amount = 500000
        #     client = razorpay.Client(
        #     auth=("rzp_test_oRlyX5LhXmmXeJ", "6zxeEQafauF3o4awwAkWYat1"))
        #     payment = client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture': '1'})
        #     return redirect('razorpay_success')
        #     #return render(request, 'evara-frontend/razorpay_name.html')
            

# class order_summary(View):
#     def get(self, request):


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import CartItem

@require_POST
def update_cart_item(request, cart_item_id):
    try:
        print("Request received")
        print(f"Request method: {request.method}")
        print(f"Request data: {request.body}")
        print(f"Request headers: {request.headers}")

        cart_item = CartItem.objects.get(id=cart_item_id)

        new_quantity = int(request.POST.get('quantity'))
        print(f"New quantity: {new_quantity}")
        cart_item.quantity = new_quantity
        print(cart_item_id,new_quantity)
        cart_item.save()
        return JsonResponse({'success': True})
    except CartItem.DoesNotExist:
        return JsonResponse({'error': 'Cart item not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid quantity'}, status=400)