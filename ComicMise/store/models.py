from django.db import models
from category.models import Category
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from PIL import Image

# Create your models here.
class YourModelManager(models.Manager):
    def get_primary_key_by_name(self, name):
        try:
            obj = self.get(product_name=name)
            return obj.pk
        except Category.DoesNotExist:
            return None

class Product(models.Model):
    product_name    = models.CharField(max_length=200, unique=True)
    slug            = models.SlugField(max_length=200, unique=True)
    description     = models.TextField(max_length=500, blank=True)
    promotion_price = models.IntegerField()
    
    is_available    = models.BooleanField(default=True)
    category        = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date    = models.DateTimeField(auto_now_add=True)
    modified_date   = models.DateTimeField(auto_now=True)
    popularity      = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    average_rating  = models.DecimalField(max_digits=3, decimal_places=1, default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    regular_price = models.IntegerField(null=True, blank=True) 

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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)

        target_width = 510
        target_height = 600

        width, height = img.size
        aspect_ratio = width / height

        # Calculate the cropping box
        if width / height > target_width / target_height:
            # Image is wider than the target aspect ratio
            new_width = int(height * (target_width / target_height))
            left = (width - new_width) / 2
            top = 0
            right = left + new_width
            bottom = height
        else:
            # Image is taller than the target aspect ratio
            new_height = int(width * (target_height / target_width))
            left = 0
            top = (height - new_height) / 2
            right = width
            bottom = top + new_height

        # Crop the image
        img = img.crop((left, top, right, bottom))

        # Resize the image to the target dimensions
        img = img.resize((target_width, target_height), Image.BICUBIC)

        # Save the cropped and resized image back to the same path
        img.save(self.image.path)

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     img = Image.open(self.image.path)

        # if img.height > 300 or img.width > 300:
        #     output_size = (300,300)
        #     img.thumbnail(output_size)
        #     img.save(self.image.path)

class Variants(models.Model):
    variant = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.variant
    
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