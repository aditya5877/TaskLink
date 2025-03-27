# D:\TaskLink\TaskLink\MyApp\admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, WorkerReview

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_worker', 'worker_type', 'location', 'is_subscribed', 'is_otp_verified', 'is_staff')
    list_filter = ('is_worker', 'worker_type', 'is_subscribed', 'is_otp_verified', 'is_staff')  # Removed police_verification, gender
    search_fields = ('username', 'email', 'first_name', 'last_name', 'location', 'worker_type')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email', 'mobile_number', 'location')
        }),
        ('Worker Info', {
            'fields': ('is_worker', 'worker_type', 'experience', 'profile_picture')
        }),
        ('Subscription Info', {
            'fields': ('is_subscribed', 'subscription_date')
        }),
        ('OTP Info', {
            'fields': ('otp', 'is_otp_verified')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'mobile_number', 'location', 
                       'is_worker', 'worker_type', 'experience', 'is_subscribed', 'password1', 'password2'),
        }),
    )
    
    ordering = ('username',)
    readonly_fields = ('last_login', 'date_joined', 'otp', 'is_otp_verified')

class WorkerReviewAdmin(admin.ModelAdmin):
    list_display = ('worker', 'reviewer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('worker__username', 'reviewer__username', 'comment')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(WorkerReview, WorkerReviewAdmin)