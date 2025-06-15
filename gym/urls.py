from django.urls import path
from . import views

app_name = 'gym'

urlpatterns = [
    # Home
    path('', views.index, name='index'),
    
    # Authentication
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    # path('accounts/register/', views.register_view, name='register'),
    
    # Devices
    path('devices/', views.device_list, name='device_list'),
    path('devices/create/', views.device_create, name='device_create'),
    path('devices/<int:device_id>/', views.device_detail, name='device_detail'),
    path('devices/<int:device_id>/edit/', views.device_edit, name='device_edit'),
    path('devices/<int:device_id>/delete/', views.device_delete, name='device_delete'),
    
    # Plans
    path('plans/', views.plan_list, name='plan_list'),
    path('plans/create/', views.plan_create, name='plan_create'),
    path('plans/<int:plan_id>/', views.plan_detail, name='plan_detail'),
    path('plans/<int:plan_id>/edit/', views.plan_edit, name='plan_edit'),
    path('plans/<int:plan_id>/delete/', views.plan_delete, name='plan_delete'),
    path('plans/<int:plan_id>/add_device/', views.plan_add_device, name='plan_add_device'),
    path('plans/<int:plan_id>/remove_device/<int:plan_device_id>/', views.plan_remove_device, name='plan_remove_device'),
    path('plans/<int:plan_id>/reorder_devices/', views.plan_reorder_devices, name='plan_reorder_devices'),
    
    # Sessions
    path('sessions/', views.session_list, name='session_list'),
    path('sessions/start/', views.session_start, name='session_start'),
    path('sessions/<int:session_id>/', views.session_detail, name='session_detail'),
    path('sessions/<int:session_id>/close/', views.session_close, name='session_close'),
    path('sessions/<int:session_id>/cancel/', views.session_cancel, name='session_cancel'),
    path('sessions/<int:session_id>/device/<int:device_session_id>/', views.device_session_update, name='device_session_update'),
    path('sessions/<int:session_id>/device/<int:device_session_id>/mark_done/', views.device_session_mark_done, name='device_session_mark_done'),
    path('sessions/<int:session_id>/device/<int:device_session_id>/mark_undone/', views.device_session_mark_undone, name='device_session_mark_undone'),
    
    # User Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]