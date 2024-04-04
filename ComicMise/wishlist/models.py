from django.db import models
from accounts.models import Account
from store.models import Product, ProductVariation

# Create your models here.
class wishlist(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)

class wishlist_item(models.Model):
    wishlist = models.ForeignKey(wishlist, on_delete=models.CASCADE, related_name='wishlist_items')
    product     = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations  = models.ManyToManyField(ProductVariation, blank=True)
    is_active   = models.BooleanField(default=True)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product