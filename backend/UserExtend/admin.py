from django.contrib import admin
from .models import UserInfo

# Register your models here.

admin.site.register(UserInfo)

class UserInfoAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_active',)