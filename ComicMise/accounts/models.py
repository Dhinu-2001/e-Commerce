from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth import get_user_model
import uuid
from django.utils import timezone

# Create your models here.

# superuser email=dhinu123@gmail.com
# password= dhinu123
class Address(models.Model):
    address_title = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    ph_number = models.IntegerField()
    pincode = models.CharField(max_length=50)
    locality = models.CharField(max_length=50)
    address = models.TextField(max_length=500)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    landmark = models.CharField(max_length=50)
    alt_phone_number = models.IntegerField()

class MyAccountManager(BaseUserManager):
    def create_user(self,username, first_name, last_name, email, password=None):
        if not email:
            raise ValueError('User must have an email address')
        if not username:
            raise ValueError('User must have an username')
        
        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, username, password):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            password = password,
            first_name = first_name,
            last_name = last_name,
        )
        user.is_active = True
        user.is_user = True
        user.is_admin = True
        user.save(using=self._db)
        return user

class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=50)
    addresses = models.ManyToManyField(Address, related_name='account_addresses')
    # required
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_user = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = MyAccountManager()

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, add_label):
        return True

User = get_user_model()

# Create your models here.
class Profile(models.Model):
    user=models.OneToOneField(Account,   on_delete=models.CASCADE,related_name="profile")
    phone_number=models.CharField(max_length=15, default='')
    otp = models.CharField(max_length=100, null=True, blank=True)
    uid=models.CharField(default=f'{uuid.uuid4}',max_length=200)
    otp_expiry = models.DateTimeField(default=timezone.now)

