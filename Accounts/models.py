from django.db import models

class user(models.Model):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    email= models.EmailField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    address= models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    

    def __str__(self):
        return self.username, self.email, self.first_name, self.last_name, self.password