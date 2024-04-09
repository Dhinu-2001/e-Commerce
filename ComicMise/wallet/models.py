from django.db import models
from accounts.models import Account

# Create your models here.
class Wallet(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} wallet"
    