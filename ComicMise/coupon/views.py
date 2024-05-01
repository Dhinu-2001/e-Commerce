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
        valid_from_str = request.POST.get('valid_from')
        valid_to_str = request.POST.get('valid_to')
        discount = request.POST.get('discount')
        active = request.POST.get('is_active',False)
        if not code or not valid_from_str or not valid_to_str or not discount:
            messages.error(request, 'Enter the all fields.')
            return render(request, 'evara-backend/add_coupon.html')
        
        print(valid_from_str, valid_to_str)
        errors = {}
        if ' ' in set(code) and len(set(code)) == 1:
            errors['code'] ="Code name cannot contain only white space"
        if len(code) <= 2:
            errors['code'] ="Code name must be longer than 2 characters."

        # valid_from = datetime.strptime(valid_from_str, '%Y-%m-%d')
        # valid_to = datetime.strptime(valid_to_str, '%Y-%m-%d')

        if valid_to_str < valid_from_str:
            errors['valid_to'] ="'Valid to' date cannot be less than 'Valid from' date."

        # valid_to = datetime.strptime(valid_to_str, '%Y-%m-%dT%H:%M')
        if errors:
            return render(request, 'evara-backend/add_coupon.html', {'errors': errors})
        else:
            coupon_submit = Coupon(
                code       = code,
                valid_from = valid_from_str,
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