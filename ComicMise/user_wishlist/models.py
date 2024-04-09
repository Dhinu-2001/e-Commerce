from django.db import models
from accounts.models import Account
from store.models import Product

# Create your models here.
class User_wishlist(models.Model):
    user        = models.ForeignKey(Account,on_delete=models.CASCADE,  related_name='user_wishlist')
    products    = models.ManyToManyField(Product, related_name='user_wishlist')
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Wish List"
