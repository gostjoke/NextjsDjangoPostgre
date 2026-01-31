from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='supervised_departments')
    

    def __str__(self):
        return self.name


class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    department = models.ForeignKey(department, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username