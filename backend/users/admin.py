from backend.settings import ADMIN_EMPTY_VALUE
from django.contrib import admin

from .models import Subscription, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'email', 'username', 'password', 'first_name',
                    'last_name')
    list_editable = ('password', )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email')
    empty_value_display = ADMIN_EMPTY_VALUE


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    list_editable = ('user', 'author')
    search_fields = ('user', 'author')
    empty_value_display = ADMIN_EMPTY_VALUE
