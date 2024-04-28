from django.utils import timezone
from django.shortcuts import redirect, render
from django.views import View
from datetime import datetime
from django.contrib import messages
from coupon.models import Coupon
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
# Create your views here.

def is_admin(user):
    return user.is_admin

@method_decorator(user_passes_test(is_admin), name='dispatch')
class add_coupon(View):
    def get(self, request):
        return render(request, 'evara-backend/add_coupon.html')
    
    def post(self, request):
        code = request.POST.get('code')
        valid_from = request.POST.get('valid_from')
        valid_to_str = request.POST.get('valid_to')
        discount = request.POST.get('discount')
        active = request.POST.get('is_active',False)
        print(active)
        if not code or not valid_from or not valid_to_str or not discount:
            messages.error(request, 'Enter the required fields.')
            return render(request, 'evara-backend/add_coupon.html')
        print(valid_to_str)
        # valid_to = datetime.strptime(valid_to_str, '%Y-%m-%dT%H:%M')

        # if timezone.now() > valid_to:
        #     messages.error(request, 'Valid to date must start from tomorrow.')
        #     return render(request, 'evara-backend/add_coupon.html')

        coupon_submit = Coupon(
            code       = code,
            valid_from = valid_from,
            valid_to   = valid_to_str,
            discount   = discount,
            active     = active
        )
        coupon_submit.save()
        return redirect('add_coupon')

@method_decorator(user_passes_test(is_admin), name='dispatch')
class coupon_list(View):
    def get(self, request):
        coupon_list = Coupon.objects.all().order_by('-valid_from')
        context = {
            'coupon_list': coupon_list
        }
        return render(request,'evara-backend/coupon_list.html',context)

@method_decorator(user_passes_test(is_admin), name='dispatch')
class coupon_action(View):
    def get(self, request, coupon_id):
        coupon = Coupon.objects.get(id = coupon_id)
        if coupon.active is True:
            coupon.active = False
            coupon.save()
        else:
            coupon.active = True
            coupon.save()
        return redirect('coupon_list')
    
class remove_coupon(View): #remove function of coupon in User cart..................
    def get(self, request):
        coupon_code = request.session.pop('coupon_code', None)
        return redirect('cart')