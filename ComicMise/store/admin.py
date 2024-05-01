from django.contrib import admin
from .models import Product, ProductImage, Variants, ProductVariation
# Register your models here.

admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Variants)
admin.site.register(ProductVariation)