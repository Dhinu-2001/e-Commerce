from django.shortcuts import render

# Create your views here.
from django.views import View
import razorpay
from django.views.decorators.csrf import csrf_exempt

from cart.models import OrderItem, Order
from accounts.models import Account
   
def razorpay_name( request, order_id):
    user_id = request.session['user_id']
    user = Account.objects.get( id = user_id)
    order = Order.objects.get(id = order_id )
    data_amount = order.total_price * 100
    if request.method == "POST":
        
        amount = data_amount
        client = razorpay.Client(
            auth=("rzp_test_oRlyX5LhXmmXeJ", "6zxeEQafauF3o4awwAkWYat1"))
        payment = client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture': '1'})
    context ={
        'user_name':user.username,
        'user_id':user_id,
        'order_id':order_id,
        'order' : order,
        'data_amount':data_amount,
    }
    return render(request, 'reid/razorpay_name.html',context)

@csrf_exempt
def razorpay_success(request, user_id, order_id):
    user = Account.objects.get(id = user_id)
    order_id = Order.objects.get(id = order_id)
    
    order_items = OrderItem.objects.filter(order = order_id)
    order_items_variations=[]
    for order_item in order_items:
        variations = order_item.variations.all()
        for variation in variations:
            order_items_variations.append((order_item, variation))

    context={
            'order_no': order_id.id,
            'order_date': order_id.order_date,
            'order_method': order_id.payment_method,
            'shipping_address': order_id.shipping_address,
            'order_items_variations':order_items_variations,
            'total':order_id.total_price,
            'user_name':user.username  
        }
    return render(request, 'reid/order_success.html',context)