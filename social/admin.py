from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, Message


admin.site.register(User, UserAdmin)

# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ['username', 'password', 'following_count', 'follower_count']
#     ordering = ['username']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['text', 'member_check']
    ordering = ['text']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['time', 'sender', 'recip', 'text', 'public']
    ordering = ['-time']
