from django.contrib import admin
from .models import Device, Plan, PlanDevice, Session, DeviceSession

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at')
    list_filter = ('created_by',)
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at'

class PlanDeviceInline(admin.TabularInline):
    model = PlanDevice
    extra = 1

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    list_filter = ('user',)
    search_fields = ('name',)
    date_hierarchy = 'created_at'
    inlines = [PlanDeviceInline]

class DeviceSessionInline(admin.TabularInline):
    model = DeviceSession
    extra = 0

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'plan', 'start_time', 'end_time', 'status')
    list_filter = ('user', 'status')
    search_fields = ('plan__name', 'user__username')
    date_hierarchy = 'start_time'
    inlines = [DeviceSessionInline]

@admin.register(DeviceSession)
class DeviceSessionAdmin(admin.ModelAdmin):
    list_display = ('device', 'session', 'performed', 'weight', 'sets', 'moves_per_set')
    list_filter = ('performed', 'session__user')
    search_fields = ('device__name', 'session__user__username')