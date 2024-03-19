from django.db import models
from accounts.models import Account
from store.models import Product, ProductVariation

# Create your models here.
class Cart(models.Model):
    cart_id     = models.CharField(max_length=250, blank=True)
    date_added  = models.DateField(auto_now_add=True)

    def _str_(self):
        return self.cart_id
    

class CartItem(models.Model):
    product     = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations  = models.ManyToManyField(ProductVariation, blank=True)
    cart        = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity    = models.IntegerField()
    is_active   = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.price * self.quantity

    def _str_(self):
        return self.product