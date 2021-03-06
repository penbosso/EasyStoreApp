from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.conf import settings
import re


def validate_product_name(prodname):
    regex_string = r'^\w[\w ]*$'
    search = re.compile(regex_string).search
    result = bool(search(prodname))
    if not result:
        raise ValidationError("Please only use letters, "
                              "numbers and underscores or spaces. "
                              "The name cannot start with a space.")


class Product(models.Model):
    name = models.CharField(max_length=100,
                            validators=[validate_product_name])
    
    cost_price = models.DecimalField(max_digits=7,
                                      decimal_places=2,
                                      default=0)
    price = models.DecimalField(max_digits=7, 
                                      decimal_places=2,
                                      default=0)
    stock_applies = models.BooleanField(default=True)
    stock = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["-stock"]

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        """
        Returns the url to access a particular product instance.
        """
        return reverse('product-detail', args=[str(self.id)])
    

    def clean(self):
        validate_product_name(self.name)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.full_clean()
        return super(Product, self).save(*args, **kwargs)


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10,
                                      decimal_places=2,
                                      default=0)
    profit = models.DecimalField(max_digits=10,
                                      decimal_places=2,
                                      default=0)
    
    done = models.BooleanField(default=False)
    last_change = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('view_order', args=[self.id])

    def __str__(self):
        return "Transact on: {:%B %d, %Y; %H:%M}".format(self.last_change)


class Cash(models.Model):
    amount = models.DecimalField(max_digits=10,
                                 decimal_places=2,
                                 default=0)
    cost  = models.DecimalField(max_digits=10,
                                      decimal_places=2,
                                      default=0)


class Order_Item(models.Model):
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    name = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now=True)

class Purchase(models.Model):
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE)
    cost_price = models.DecimalField(max_digits=7, decimal_places=2)
    selling_price = models.DecimalField(max_digits=7, decimal_places=2)
    stock = models.PositiveSmallIntegerField()
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["timestamp"]

    def save(self, *args, **kwargs):
        if(self.cost_price != 0):
            self.product.cost_price = self.cost_price
        if(self.selling_price != 0):
            self.product.price = self.selling_price
        self.product.stock = int(self.product.stock) + self.stock
        self.product.save()
        return super(Purchase, self).save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Returns the url to access a particular product instance.
        """
        return reverse('product-detail', args=[str(self.id)])

    def __str__(self):
        return "Purchase on: {:%B %d, %Y; %H:%M}".format(self.timestamp) 

class OtherPurchase(models.Model):
    item_name = models.CharField(max_length=100)
    cost_price = models.DecimalField(max_digits=7, decimal_places=2)
    receipt = models.CharField(max_length=100, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["timestamp"]

    def get_absolute_url(self):
        """
        Returns the url to access a particular product instance.
        """
        return reverse('product-detail', args=[str(self.id)])

    def __str__(self):
        return "Purchase on: {:%B %d, %Y; %H:%M}".format(self.timestamp) 

class Setting(models.Model):
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=100)

    def __str__(self):
        return self.key

    def __bool__(self):
        return bool(self.value)

    __nonzero__ = __bool__