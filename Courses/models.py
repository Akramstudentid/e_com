from django.db import models
from django.conf import settings
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
    keywords = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    docs = models.FileField(upload_to='courses/docs/', null=True, blank=True)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    offer = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField(default=0)
    available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    video_url = models.URLField(null=True, blank=True)
    thumbnail = models.ImageField(upload_to='courses/thumbnails/', null=True, blank=True)

    images = models.JSONField(default=list, blank=True)

    @property
    def offer_price(self):
        if self.offer:
            return self.mrp - (self.mrp * self.offer / 100)
        return self.mrp

    def __str__(self):
        return self.name

class Offer(models.Model):
    OFFER_TYPES = (
        ('regular', 'Regular'),
        ('occasional', 'Occasional'),
        ('first_time', 'First Time'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
        )

    title = models.CharField(max_length=255)
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPES)
    discount_percentage = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
from django.db import models
from django.conf import settings

class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True  
    )
    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        #calculate total price based on course price and quantity
        price = self.course.offer_price if self.course.offer_price else self.course.mrp
        self.total_price = price * self.quantity

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} - {self.course.name}"

class Login(models.Model):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.username
    
