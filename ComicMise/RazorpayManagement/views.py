from django.http import HttpResponse
from django.shortcuts import render, redirect
# Create your views here.
from django.views import View
from django.conf import settings
import razorpay
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
from django.views.decorators.csrf import csrf_exempt
from cart.models import Cart, OrderItem, Order

@csrf_exempt
def handlerequest(request):
    if request.method == 'POST':
        try:
            payment_id = request.POST.get('razorpay_payment_id','')
            order_id = request.POST.get('razorpay_order_id','')
            signature = request.POST.get('razorpay_signature','')

            print(payment_id)
            print( order_id) 
            print( signature)
            params_dict = { 
            'razorpay_order_id': order_id, 
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature,
            }
            try:
                order_db = Order.objects.get(razorpay_order_id=order_id)
            except:
                
                order_id_session = request.session.get('order_id', 1)
                print(order_id_session)
                return redirect('razorpay_success', order_id=order_id_session)
            print(order_db)
            order_db.razorpay_payment_id = payment_id
            order_db.razorpay_signature = signature
            order_db.save()

            result = razorpay_client.utility.verify_payment_signature(params_dict)
            print(result)

            choice_set = Order.PAYMENT_STATUS_CHOICES
            if result:
                amount = order_db.total_price * 100   #we have to pass in paisa
                print(amount)
                for i in choice_set:
                        print(i[0],i[1])
                try:
                    print('succ')
                    # razorpay_client.payment.capture(payment_id, amount)
                    payment_status = [choice[0] for choice in choice_set if choice[1] == 'Success']
                    print(payment_status[0])
                    order_db.payment_status=payment_status[0]
                    order_db.save()
                    print(1)
                    return redirect('razorpay_success', order_id=order_db.id)
                except:
                    payment_status = [choice[0] for choice in choice_set if choice[1] == 'Failure']
                    print(payment_status[0])
                    order_db.payment_status=payment_status[0]
                    order_db.save()
                    print(2)
                    return redirect('razorpay_success', order_id=order_db.id)
            else:
                payment_status = [choice[0] for choice in choice_set if choice[1] == 'Failure']
                print(payment_status[0])
                order_db.payment_status=payment_status[0]
                order_db.save()
                print(3)

            return redirect('razorpay_success', order_id=order_db.id)
        except:
            choice_set = Order.PAYMENT_STATUS_CHOICES
            payment_status = [choice[0] for choice in choice_set if choice[1] == 'Failure']
            print(payment_status[0])
            order_db.payment_status=payment_status[0]
            order_db.save()
            print(4)
            order_id_session = request.session.get('order_id', 1)
            print(order_id_session)
            return redirect('razorpay_success', order_id=order_id_session)

def cart_id(request):
    cart_id= request.session.session_key
    if not cart_id:
        cart_id = request.session.create()
    return cart_id

def razorpay_success(request,  order_id):
    user = request.user
    order_id_session = request.session.get('order_id',2)
    print(order_id_session)
    order = Order.objects.get(id = order_id_session)
    if order_id == 1:
        choice_set = Order.PAYMENT_STATUS_CHOICES
        payment_status = [choice[0] for choice in choice_set if choice[1] == 'Failure']
        print(payment_status[0])
        order.payment_status=payment_status[0]
        order.save()
        print(4)
    
    order_items = OrderItem.objects.filter(order = order)
    order_items_variations=[]
    for order_item in order_items:
        variations = order_item.variations.all()
        for variation in variations:
            order_items_variations.append((order_item, variation))

#============= Handling session saved objects- Cart, Order, Coupon, Stock 
    order_items = OrderItem.objects.filter(order = order) #====== Stock updating
    if (len(order_items)>0):
        for order_item in order_items: 
            for i in order_item.variations.all():
                i.stock -= order_item.quantity
                print(i.stock, order_item.quantity)
                i.save()
    delete_currentCartOfSession = Cart.objects.get(cart_id = cart_id(request))
    print(delete_currentCartOfSession.id)
    delete_currentCartOfSession.delete()
    delete_order_id_session = request.session.pop('order_id', None)
    delete_coupon_code_session = request.session.pop('coupon_code', None)
    delete_discount_total = request.session.pop('discount_total', None)

    context={
            'order':order,
            'order_submit':order,
            'order_no': order.id,
            'order_date': order.order_date,
            'payment_method': order.payment_method,
            'shipping_address': order.shipping_address,
            'order_items_variations':order_items_variations,
            'total':order.total_price,
            'user_name':user.username  
        }
    return render(request, 'reid/order_success.html',context)