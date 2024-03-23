from django.db import models
from accounts.models import Account, Address
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
    

class Order(models.Model):

    # Payment Method Choices
    CASH_ON_DELIVERY = 'COD'
    PAYPAL = 'PayPal'
    
    PAYMENT_METHOD_CHOICES = [
        (CASH_ON_DELIVERY, 'Cash on Delivery'),
        (PAYPAL, 'PayPal'),
    ]

     # Order Status Choices
    PENDING = 'Pending'
    PROCESSING = 'Processing'
    SHIPPED = 'Shipped'
    DELIVERED = 'Delivered'
    
    ORDER_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (SHIPPED, 'Shipped'),
        (DELIVERED, 'Delivered'),
    ]

    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default=CASH_ON_DELIVERY) 
    order_date = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default=PENDING)
    shipping_address = models.ForeignKey(Address, on_delete=models.CASCADE)
    canceled = models.BooleanField(default=False)

    def _str_(self):
        return f"Order #{self.id} - {self.user.username}"

    def calculate_total_price(self):
        total_price = sum(item.price * item.quantity for item in self.orderitem_set.all())
        return total_price
    


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations  = models.ManyToManyField(ProductVariation, blank=True)
    quantity = models.PositiveIntegerField()
    price = models.IntegerField()
    
    def _str_(self):
        return f"{self.qty} x {self.product.title} in Order #{self.order.id}"