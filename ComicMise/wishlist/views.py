from django.shortcuts import render, redirect
from django.views import View
from accounts.models import Account
from .models import Wishlist
from store.models import Product
# Create your views here.
class wish(View):
    def get(self, request):
        user_id = request.session.get('user_id')
        user = Account.objects.get(id = user_id)

        try:
            wishlist = Wishlist.objects.get(user = user)
        except Wishlist.DoesNotExist:
            wishlist = Wishlist.objects.create(user = user)
        wishlist.save()
        context={
            'user_name':user.username,
            'wishlist':wishlist,
        }
        return render(request,'reid/wishlist.html',context)

class add_wish(View):
    def get(self, request, product_id):
        user_id = request.session.get('user_id')
        user = Account.objects.get(id = user_id)

        product = Product.objects.get(id = product_id)

        try:
            wishlist = Wishlist.objects.get(user = user)
        except Wishlist.DoesNotExist:
            wishlist = Wishlist.objects.create(user = user)
        wishlist.product = product
        wishlist.save()
        return redirect('wishlist')