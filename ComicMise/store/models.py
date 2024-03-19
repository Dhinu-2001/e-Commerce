from django.db import models
from category.models import Category
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class YourModelManager(models.Manager):
    def get_primary_key_by_name(self, name):
        try:
            obj = self.get(product_name=name)
            return obj.pk
        except Category.DoesNotExist:
            return None

class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug         = models.SlugField(max_length=200, unique=True)
    description  = models.TextField(max_length=500, blank=True)
    price        = models.IntegerField()
    
    is_available = models.BooleanField(default=True)
    category     = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date= models.DateTimeField(auto_now=True)
    popularity   = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])

    objects = YourModelManager()


    def save(self):
        # Generate slug if it's not provided
        if not self.slug:
            self.slug = slugify(self.product_name)
        super().save()

    def __str__(self):
        return self.product_name
    
    def get_url(self):
        # prod=ProductVariation.objects.get(product=self.id, )  
        return reverse('product_detail', args=[self.category.slug, self.slug, 'small'])
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='photos/products')


class ProductVariation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=50)
    stock = models.IntegerField(default=0)

# class SizeVariant(models.Model):
#     size = models.CharField(max_length=50)

# class ProductVariantStock(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     size = models.ForeignKey(SizeVariant, on_delete=models.CASCADE)
#     stock = models.IntegerField(default=0)

#     class Meta:
#         unique_together = ('product', 'size')