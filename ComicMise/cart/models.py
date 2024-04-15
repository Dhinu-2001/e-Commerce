from django.db import models
from accounts.models import Account, Address
from store.models import Product, ProductVariation
from coupon.models import Coupon

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
        return self.product.promotion_price * self.quantity

    def _str_(self):
        return self.product
    

class Order(models.Model):

    # Payment Method Choices
    CASH_ON_DELIVERY = 'COD'
    WALLET = 'Wallet'
    RAZORPAY = 'Razorpay'
    
    PAYMENT_METHOD_CHOICES = [
        (CASH_ON_DELIVERY, 'Cash on Delivery'),
        (WALLET, 'Wallet'),
        (RAZORPAY, 'Razorpay'),
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

     # Return Status Choices
    NOT_RETURNED = 'NOT_RETURNED'
    PROCESSING = 'PROCESSING'
    RETURNED = 'RETURNED'
    
    RETURN_STATUS_CHOICES = [
        (NOT_RETURNED, 'Not returned'),
        (PROCESSING, 'Processing'),
        (RETURNED, 'Returned'),
    ]

    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default=CASH_ON_DELIVERY) 
    order_date = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default=PENDING)
    shipping_address = models.ForeignKey(Address, on_delete=models.CASCADE)
    total_price = models.IntegerField(default=0)
    price_without_discount = models.IntegerField(default=0)
    price_discounted = models.IntegerField(default=0)
    canceled = models.BooleanField(default=False)
    is_returned = models.CharField(max_length=20, choices=RETURN_STATUS_CHOICES, default=NOT_RETURNED)
    returned_at = models.DateTimeField(blank=True, null=True)
    return_reason = models.TextField(blank=True)
    coupon_used = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    def _str_(self):
        return f"Order #{self.id} - {self.user.username}"
    # def __str__(self):
    #     return f"Order #{self.id} - {self.user.username}"


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