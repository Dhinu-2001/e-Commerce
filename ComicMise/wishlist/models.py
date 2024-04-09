from django.db import models
from accounts.models import Account
from store.models import Product

# Create your models here.
class Wishlist(models.Model):
    user        = models.ForeignKey(Account,on_delete=models.CASCADE,  related_name='wishlists')
    products = models.ManyToManyField(Product, related_name='wishlists')
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Wish List"
