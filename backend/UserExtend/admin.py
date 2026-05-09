from django.contrib import admin
from .models import UserInfo, department


# UserInfo admin (要先定義 class 再 register)
@admin.register(UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone', 'location', 'department')
    search_fields = ('user__username', 'user__email', 'phone', 'location')
    list_filter = ('department',)


@admin.register(department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'supervisor')
    search_fields = ('name',)
