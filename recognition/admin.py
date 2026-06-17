from django.contrib import admin

from .models import EmployeeProfile, Recognition, Redemption, RewardItem


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = (
        'display_name',
        'employee_id',
        'role',
        'department',
        'designation',
        'monthly_token_allowance',
        'tokens_sent_this_month',
    )
    list_filter = ('role', 'department')
    search_fields = ('user__first_name', 'user__last_name', 'user__username', 'employee_id')


@admin.register(Recognition)
class RecognitionAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'tokens', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('sender__user__first_name', 'receiver__user__first_name', 'message')


@admin.register(RewardItem)
class RewardItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'points_required', 'stock', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')


@admin.register(Redemption)
class RedemptionAdmin(admin.ModelAdmin):
    list_display = ('employee', 'reward', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('employee__user__first_name', 'employee__user__email', 'reward__name')
