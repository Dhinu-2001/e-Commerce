from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from . models import Cart, CartItem, Order, OrderItem
from store.models import Product, ProductVariation
from accounts.models import Account, Address
from django.contrib import messages
from django.http import HttpResponse
import razorpay 
from django.views.decorators.csrf import csrf_exempt
from coupon.models import Coupon
from wallet.models import Wallet
from django.middleware.csrf import get_token
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


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
        try:
            variant = ProductVariation.objects.get(product=product, size=size)
        except:
            messages.error(request, 'Selected size of product is not available.')
            return redirect('product_detail' , category_slug=product.category.slug, product_slug=product.slug, size='small')
       
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
            user_id = request.session.get('user_id')  # Use get method to avoid KeyError
            user = None  # Initialize user to None

            if user_id is not None:  # Check if user_id exists
                user = get_object_or_404(Account, pk=user_id)

            try:
                cart = Cart.objects.get(cart_id = cart_id(request))
            except Cart.DoesNotExist:
                cart = Cart.objects.create(cart_id = cart_id(request))
            cart.save()
            cart_items = CartItem.objects.filter(cart = cart, is_active=True)
            cart_items_variations = []
            
            coupon_list = Coupon.objects.filter(valid_to__gte=timezone.now(),active=True)

            for cart_item in cart_items:
                total_price += (cart_item.product.promotion_price * cart_item.quantity)
                quantity += cart_item.quantity
                variations = cart_item.variations.all()
                for variation in variations:
                    print(variation.size)
                    cart_items_variations.append((cart_item, variation))
            coupon_code = request.POST.get('coupon_code', None)
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
            context = {
            'cart_total':total_price,
            'total': total_grand,
            'coupon_list':coupon_list,
            
            'coupon_code':coupon_code,
            'quantity':quantity,
            'cart_items_variations': cart_items_variations,
            'user_id':user_id,
            'user': user,
            'csrf_token': get_token(request)
        }
        
               
        except Cart.DoesNotExist:
            
            pass
      
        
        return render(request, 'reid/cart.html',context)
    
    def post(self,request, total_price=0, quantity=0, cart_items=None):
        try:
            user_id = request.session.get('user_id')  # Use get method to avoid KeyError
            user = None  # Initialize user to None

            if user_id is not None:  # Check if user_id exists
                user = get_object_or_404(Account, pk=user_id)

            cart = Cart.objects.get(cart_id=cart_id(request))
            print('1'+cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart, is_active=True)
            cart_items_variations = []
            coupon_list = Coupon.objects.filter(valid_to__gte=timezone.now(),active=True)

            for cart_item in cart_items:
                total_price += (cart_item.product.promotion_price * cart_item.quantity)
                quantity += cart_item.quantity
                variations = cart_item.variations.all()
                for variation in variations:
                    print(variation.size)
                    cart_items_variations.append((cart_item, variation))
            coupon_code = request.POST.get('coupon_code', None)
            coupon = None
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
            'coupon':coupon,
            'coupon_code':coupon_code,
            'quantity':quantity,
            'cart_items_variations': cart_items_variations,
            'user_id':user_id,
            'user': user,
        }
        
        return render(request, 'reid/cart.html',context)

@method_decorator(login_required(login_url='login'), name='dispatch')
class place_order(View):
    def get(self, request, total_price=0, quantity=0, cart_items=None):
        user_id = request.session.get('user_id')  # Use get method to avoid KeyError
        user = None  # Initialize user to None

        if user_id is not None:  # Check if user_id exists
            user = get_object_or_404(Account, pk=user_id)

        addresses = user.addresses.all()
        try:
            cart = Cart.objects.get(cart_id=cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart, is_active=True)
            if len(cart_items) == 0:
                messages.error(request, 'Your cart is empty!')
                return redirect('cart')
            cart_items_variations = []
            for cart_item in cart_items:
                total_price += (cart_item.product.promotion_price * cart_item.quantity)
                quantity += cart_item.quantity
                variations = cart_item.variations.all()
                for variation in variations:
                    print(variation.size)
                    cart_items_variations.append((cart_item, variation))
            
            coupon_code_session = request.session.get('coupon_code')
            try:
                coupon_code = Coupon.objects.get(code = coupon_code_session)
            except:
                coupon_code = None

            if coupon_code is not None:
                total_grand = request.session.get('discount_total')
            else:
                total_grand = total_price
        except Cart.DoesNotExist:
            pass

        try:
            wallet = Wallet.objects.get(user = user)
        except Wallet.DoesNotExist:
            wallet = Wallet.objects.create(user = user)
            wallet.save()
        wallet_balance = wallet.amount
        
        context = {
            'cart_total':total_price,
            'total': total_grand,
            'quantity':quantity,
            'cart':cart.id,
            'cart_items_variations': cart_items_variations,
            'user_id':user_id,
            'user': user,
            'addresses': addresses,
            'coupon_code':coupon_code,
            'wallet_balance':wallet_balance,
        }
        return render(request, 'reid/checkout.html',context)



from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
import razorpay

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@method_decorator(login_required(login_url='login'), name='dispatch')
class order_success(View):
    @csrf_exempt
    def post(self, request, cart, user_name):
        
        payment_method = request.POST.get('payment_option')
        print(payment_method)
        # amount = 50000
            # client = razorpay.Client(
            #     auth=("rzp_test_oRlyX5LhXmmXeJ", "6zxeEQafauF3o4awwAkWYat1"))
            # payment = client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture': '1'})

#=============================== Order shipping Address Managing =======================================

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
            alt_phone_number = request.POST['alternate_phone_numbel']

# FORM VALIDATION===============================================
        # CHECKING MANDATORY FIELDS
            if not address_title or not name or not ph_number or not pincode or not locality or not address or not city or not state:
                messages.error(request,'Please, enter the required fields')
                return redirect('place_order' )
            
        # CHECKING PHONE NUMBERS
            if ph_number:
                if not ph_number.isdigit():
                    messages.error(request,'Give valid phone number.(Phone number should be integers)')
                    return redirect('place_order' ) 
                elif len(ph_number) != 10:
                    messages.error(request,'Give valid phone number.(Phone number should contain 10 digits)')
                    return redirect('place_order' )
                elif len(set(ph_number)) == 1 and ph_number[0] == '0':
                    messages.error(request, "Phone number can't contain only 0s ")
                    return redirect('place_order')
            if alt_phone_number:
                if not alt_phone_number.isdigit():
                    messages.error(request,'Give valid phone number.(Phone number should be integers)')
                    return redirect('place_order' ) 
                elif len(alt_phone_number) != 10:
                    messages.error(request,'Give valid phone number.(Phone number should contain 10 digits)')
                    return redirect('place_order' )
                elif len(set(alt_phone_number))==1 and alt_phone_number[0]=='0':
                    messages.error(request, "Phone number can't contain only 0s.")
                    return redirect('place_order')
        # CHECKING PINCODE
            if pincode:
                if not pincode.isdigit():
                    messages.error(request,'Give valid phone number.(Pin code should be integers)')
                    return redirect('place_order' ) 
                elif len(pincode) != 6:
                    messages.error(request,'Give valid phone number.(Pin code should contain 6 digits)')
                    return redirect('place_order' )
                elif len(set(pincode))==1 and pincode[0]=='0':
                    messages.error(request, "Pin code can't contain only 0s.")
                    return redirect('place_order')

            fd = Address(address_title=address_title, name=name, ph_number=ph_number, pincode=pincode, locality=locality, address=address, city=city, state=state, landmark=landmark, alt_phone_number=alt_phone_number)
            fd.save()
            user_id = request.session['user_id']
            user = Account.objects.get(pk=user_id)
            user.addresses.add(fd)
            address = fd
        else:
            address =Address.objects.get(id=deli_address_id) 
        user_id = request.session.get('user_id')  # Use get method to avoid KeyError
        user = None  # Initialize user to None

        if user_id is not None:  # Check if user_id exists
            user = get_object_or_404(Account, pk=user_id)

        # variations = 

#-------------------------------------------------Order database insertion---------------------------------------------------
        try:
            order_submit = Order.objects.get(id = request.session['order_id'])
            order_submit.payment_method = payment_method
            order_submit.shipping_address = address
            order_submit.save()
            #=============== (Modified Cart) Handling ORDER ITEM if cart is modified ===================================

            #====== If Cart is updated again Below code is for handling ORDER DB==============

            order_items = OrderItem.objects.filter(order = order_submit)
            order_items.delete() # ===== Deleting current order items for updating new ==============

            #========== Updating with (Modified Cart) ==================
            total = 0
            cart_items = CartItem.objects.filter(cart = cart, is_active=True)
            if (len(cart_items)>0):
                for cart_item in cart_items:
                    total += (cart_item.product.promotion_price * cart_item.quantity)
                    product = cart_item.product
                    variations = cart_item.variations.all()
                    print(variations)
                    quantity = cart_item.quantity
                    price = cart_item.sub_total()
            #=================== (Modified Cart) adding each CART ITEM to ORDER ITEM ============================================
                    order_item = OrderItem(
                    order = order_submit,
                    product = product,
                    quantity = quantity,
                    price = price,
                    )
                    order_item.save()
                    order_item.variations.set(cart_item.variations.all()) #===(Modified Cart) Variant allocating
                    print(order_item, order_item.variations.all())
            else:
                return HttpResponse('No product in cart') 
        except:
            order_submit = Order(user=user, payment_method=payment_method, shipping_address=address )
            order_submit.save()
            request.session['order_id'] = order_submit.id
        
            total = 0
            cart_items = CartItem.objects.filter(cart = cart, is_active=True)
            if (len(cart_items)>0):
                for cart_item in cart_items:
                    total += (cart_item.product.promotion_price * cart_item.quantity)
                    product = cart_item.product
                    variations = cart_item.variations.all()

                    quantity = cart_item.quantity
                    price = cart_item.sub_total()
    #============================================== adding each CART ITEM to ORDER ITEM ============================================
                    order_item = OrderItem(
                        order = order_submit,
                        product = product,
                        quantity = quantity,
                        price = price,
                    )
                    order_item.save()
                    order_item.variations.set(cart_item.variations.all())  #===(Modified Cart) Variant allocating
                    print(order_item, order_item.variations.all())
                    # for i in order_item.variations.all():
                    #     i.stock -= order_item.quantity
                    #     print(i.stock, order_item.quantity)
                    #     i.save()
                    # cart_item.delete( ) # ====== Deleting Cart Item====
            else:
                return HttpResponse('No product in cart')  
        
        

#================================================ Total amount saving in database ===================================

     #==============COUPON MANAGING========================
        # order_i = Order.objects.get(id = order_submit.id)
        coupon_code = request.session.get('coupon_code')
        print(coupon_code)
        try:
            coupon = Coupon.objects.get(code=coupon_code,valid_to__gte=timezone.now(),active=True)
        except Coupon.DoesNotExist:
            coupon = None
        if coupon_code is not None:
            order_submit.coupon_used = coupon
            order_submit.price_without_discount = total
            discount_total=request.session.get('discount_total')
            price_discounted = total - discount_total
            order_submit.price_discounted = price_discounted
            order_submit.total_price = discount_total
        else:
            order_submit.total_price = total
            order_submit.price_without_discount = total
            order_submit.price_discounted = 0
        # delete_coupon = request.session.pop('coupon_code', None)
        order_submit.save()

    #======================= Fetching ORDER ITEM to display on order summary =================

        order_items = OrderItem.objects.filter(order = order_submit)
        order_items_variations=[]
        for order_item in order_items:
            variations = order_item.variations.all()
            for variation in variations:
                order_items_variations.append((order_item, variation))

#=================================== WALLET CREATING=================================

        if payment_method == 'WALLET':
            wallet = Wallet.objects.get( user = user)
            wallet.amount -= order_submit.total_price
            wallet.save()

            choice_set = Order.PAYMENT_STATUS_CHOICES
            payment_status = [choice[0] for choice in choice_set if choice[1] == 'Success']
            order_submit.payment_status=payment_status[0]
            order_submit.save()
        wallet = Wallet.objects.get( user = user)


#===================================RAZORPAY HANDLING===============================================

        if payment_method == 'RAZORPAY':
            order = Order.objects.get(id = order_submit.id )
            if order.razorpay_order_id is None:
                order_currency = 'INR'
                print('before')
                notes = {'order-type':"basic order from the website"}
                receipt_maker = str(order.id)
                print(order.total_price,order_currency,notes,order.id ,receipt_maker )

                #razorpay_order = razorpay_client.order.create(dict(amount= order.total_price*100,currency=order_currency, notes=notes, receipt=order_id, payment_capture='0'))
                razorpay_order = razorpay_client.order.create(dict(
                amount=order.total_price * 100,
                currency=order_currency,
                notes=notes,
                receipt=receipt_maker,
                payment_capture='1'  # Ensure this line is inside the dictionary
                ))  
                print('after')
                print(razorpay_order['id'])
                order.razorpay_order_id = razorpay_order['id']
                print(order.razorpay_order_id, order.id)
                order.save()
            total_amount =order.total_price * 100
            callback_url = 'http://'+str(get_current_site(request))+"/razorpay/handlerequest/"
            print(callback_url)
                
            context ={
                'user_id':user_id,
                'user': user,
                'order':order,
                'razorpay_order_id':order.razorpay_order_id,
                'order_id':order.id,
                'total_amount':total_amount,
                'total_price':order.total_price,
                'razorpay_merchant_id':settings.RAZORPAY_KEY_ID,
                'callback_url':callback_url
            }
            return render(request, 'reid/razorpay_name.html',context)
           
#============= Handling session saved objects- Cart, Order, Coupon, Stock 
        order_items = OrderItem.objects.filter(order = order_submit) #====== Stock updating
        if (len(order_items)>0):
            for order_item in order_items: 
                for i in order_item.variations.all():
                    i.stock -= order_item.quantity
                    print(i.stock, order_item.quantity)
                    i.save()

        delete_currentCartOfSession = Cart.objects.get(id = cart)
        print(delete_currentCartOfSession.id)
        delete_currentCartOfSession.delete()
        delete_order_id_session = request.session.pop('order_id', None)
        delete_coupon_code_session = request.session.pop('coupon_code', None)
        delete_discount_total = request.session.pop('discount_total', None)

        context={
            'template_for':'first_payment',
            'coupon_code':coupon_code,
            'order_no': order_submit.id,
            'order_date': order_submit.order_date,
            'order_method': order_submit.payment_method,
            'order':order_submit,
            'order_submit':order_submit,
            'shipping_address': order_submit.shipping_address,
            'order_items_variations':order_items_variations,
            'total':total,
            'user_id':user_id,
            'user': user,
            'wallet':wallet, 
        }
        return render(request, 'reid/order_success.html',context)
        

#=========================================== Cart fetch ==================================================

from django.http import JsonResponse
import json
from django.views.decorators.http import require_POST
from .models import CartItem


def update_cart_item(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_quantity = data.get('quantity')
            cart_item_id = data.get('cart_item_id')

            cart_item = CartItem.objects.get(id=cart_item_id)
            
            print(new_quantity)
            print(type(new_quantity))
            cart_item.quantity = int(new_quantity)
            print(type(new_quantity))
            print(cart_item_id,new_quantity)
            cart_item.save()

            updated_subtotal = (cart_item.product.promotion_price * cart_item.quantity)
            # updated_subtotal = cart_item.sub_total()
            print(updated_subtotal)

# grand total =====================================================
            cart = Cart.objects.get(cart_id = cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart,is_active=True)
            cart_total=0
            for item in cart_items:
                cart_total += item.product.promotion_price * item.quantity
            is_coupon = request.session.get('coupon_code')
            if is_coupon is not None:
                current_time = timezone.now()
                coupon = Coupon.objects.get(code = is_coupon)
                if coupon.valid_to >= current_time and coupon.active is True:
                    discount_rate = (coupon.discount / 100) * cart_total
                    total_afer_discount = cart_total - discount_rate
                    request.session['discount_total'] = total_afer_discount
                    # request.session['coupon_code'] = coupon_code
                    grand_total = request.session.get('discount_total')
                else:
                    #!!!!!!!!!!!!!!!!!!!!!!
                    #send message 'that coupon is expired'
                    #!!!!!!!!!!!!!!!!!!!!!!
                    grand_total = cart_total
            else:
                grand_total = cart_total
                


            return JsonResponse({'success': True, 'updated_subtotal': updated_subtotal, 'updated_cart_total':cart_total, 'updated_grand_total':grand_total})
        except CartItem.DoesNotExist:
            return JsonResponse({'error': 'Cart item not found'}, status=404)
        except ValueError:
            return JsonResponse({'error': 'Invalid quantity'}, status=400)
        
@method_decorator(login_required(login_url='login'), name='dispatch')
class order_invoice(View):
    def get(self, request, order_id):
        user_id = request.session.get('user_id')  # Use get method to avoid KeyError
        user = None  # Initialize user to None

        if user_id is not None:  # Check if user_id exists
            user = get_object_or_404(Account, pk=user_id)

        print(user.username)

        order = Order.objects.get(id = order_id)
        order_items = OrderItem.objects.filter(order = order)
        context={
            'user_id':user_id,
            'user': user,
            'order':order,
            'order_items':order_items,
        }
        return render(request, 'reid/order_invoice.html', context)