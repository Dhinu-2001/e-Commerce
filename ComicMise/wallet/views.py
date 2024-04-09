from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View
from cart.models import Order
from wallet.models import Wallet
from accounts.models import Account
# Create your views here.
class return_order(View):
    def get(self,request,order_id):
        order = Order.objects.get(id = order_id)
        
        return_status = [choice[0] for choice in Order.RETURN_STATUS_CHOICES if choice[0] == 'NOT_RETURNED']
        order.is_returned = return_status[0]
        order.save()
        return redirect('userside_order_detail', order_id=order_id)

    def post(self, request, order_id):
        order = Order.objects.get(id = order_id)
        choice_set = Order.RETURN_STATUS_CHOICES
        for i in choice_set:
            print(i[0],i[1])  
        return_status = [choice[0] for choice in choice_set if choice[1] == 'Processing']
        print(return_status[0])
        order.is_returned=return_status[0]
        return_reason = request.POST.get('return_reason')
        order.return_reason = return_reason
        # order.returned_at = timezone.now()
        order.save()

        # user_id = request.session.get('user_id')
        # user = Account.objects.get(id = user_id)
        # try:
        #     wallet = Wallet.objects.get(user = user)
        #     print(wallet)
        # except Wallet.DoesNotExist:
        #     wallet = Wallet.objects.create(user = user)
        #     print(wallet)
        #     wallet.save()
        # total_price = order.total_price
        # wallet.amount += total_price
        # wallet.save()

        return redirect('userside_order_detail', order_id=order_id)