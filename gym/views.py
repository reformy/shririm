from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.utils import timezone
from django.db.models import Max

from .models import Device, Plan, PlanDevice, Session, DeviceSession, UserProfile
from .forms import DeviceForm, PlanForm, PlanDeviceForm, SessionStartForm, DeviceSessionUpdateForm, UserProfileForm

# Authentication views
def login_view(request):
    try:
        if request.method == 'POST':
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, f"Welcome back, {username}!")
                    return redirect('gym:index')
                else:
                    messages.error(request, "Invalid username or password. Please try again.")
            else:
                messages.error(request, "Please correct the errors below.")
                for field, errors in form.errors.items():
                    for error in errors:
                        if field == 'username':
                            messages.error(request, f"Username error: {error}")
                        elif field == 'password':
                            messages.error(request, f"Password error: {error}")
                        else:
                            messages.error(request, f"{error}")
        else:
            form = AuthenticationForm()
        return render(request, 'gym/auth/login.html', {'form': form})
    except Exception as e:
        messages.error(request, f"An error occurred during login: {str(e)}")
        form = AuthenticationForm()
        return render(request, 'gym/auth/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('gym:login')

def register_view(request):
    try:
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                messages.success(request, f"Account created successfully! Welcome to Shririm, {user.username}!")
                return redirect('gym:index')
            else:
                messages.error(request, "Please correct the errors below.")
                for field, errors in form.errors.items():
                    for error in errors:
                        if field == 'username':
                            messages.error(request, f"Username error: {error}")
                        elif field == 'password1':
                            messages.error(request, f"Password error: {error}")
                        elif field == 'password2':
                            messages.error(request, f"Password confirmation error: {error}")
                        else:
                            messages.error(request, f"{error}")
        else:
            form = UserCreationForm()
        return render(request, 'gym/auth/register.html', {'form': form})
    except Exception as e:
        messages.error(request, f"An error occurred during registration: {str(e)}")
        form = UserCreationForm()
        return render(request, 'gym/auth/register.html', {'form': form})

# Home view
@login_required
def index(request):
    # Get recent sessions
    recent_sessions = Session.objects.filter(user=request.user).order_by('-start_time')[:5]
    
    # Get active session if exists
    active_session = Session.objects.filter(
        user=request.user, 
        status='in_progress'
    ).first()
    
    # Get all user plans
    plans = Plan.objects.filter(user=request.user)
    
    context = {
        'recent_sessions': recent_sessions,
        'active_session': active_session,
        'plans': plans,
    }
    return render(request, 'gym/index.html', context)

# Device views
@login_required
def device_list(request):
    devices = Device.objects.filter(created_by=request.user)
    return render(request, 'gym/devices/list.html', {'devices': devices})

@login_required
def device_create(request):
    if request.method == 'POST':
        form = DeviceForm(request.POST, request.FILES)
        if form.is_valid():
            device = form.save(commit=False)
            device.created_by = request.user
            device.save()
            messages.success(request, f"Device '{device.name}' created successfully.")
            return redirect('gym:device_list')
    else:
        form = DeviceForm()
    return render(request, 'gym/devices/create.html', {'form': form})

@login_required
def device_detail(request, device_id):
    device = get_object_or_404(Device, id=device_id, created_by=request.user)
    return render(request, 'gym/devices/detail.html', {'device': device})

@login_required
def device_edit(request, device_id):
    device = get_object_or_404(Device, id=device_id, created_by=request.user)
    if request.method == 'POST':
        form = DeviceForm(request.POST, request.FILES, instance=device)
        if form.is_valid():
            form.save()
            messages.success(request, f"Device '{device.name}' updated successfully.")
            return redirect('gym:device_list')
    else:
        form = DeviceForm(instance=device)
    return render(request, 'gym/devices/edit.html', {'form': form, 'device': device})

@login_required
def device_delete(request, device_id):
    device = get_object_or_404(Device, id=device_id, created_by=request.user)
    if request.method == 'POST':
        device_name = device.name
        device.delete()
        messages.success(request, f"Device '{device_name}' deleted successfully.")
        return redirect('gym:device_list')
    return render(request, 'gym/devices/delete.html', {'device': device})

# Plan views
@login_required
def plan_list(request):
    try:
        plans = Plan.objects.filter(user=request.user)
        return render(request, 'gym/plans/list.html', {'plans': plans})
    except Exception as e:
        messages.error(request, f"An error occurred while loading plans: {str(e)}")
        return redirect('gym:index')

@login_required
def plan_create(request):
    try:
        if request.method == 'POST':
            form = PlanForm(request.POST)
            if form.is_valid():
                plan = form.save(commit=False)
                plan.user = request.user
                plan.save()
                messages.success(request, f"Plan '{plan.name}' created successfully.")
                return redirect('gym:plan_detail', plan_id=plan.id)
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error in {field}: {error}")
        else:
            form = PlanForm()
        return render(request, 'gym/plans/create.html', {'form': form})
    except Exception as e:
        messages.error(request, f"An error occurred while creating the plan: {str(e)}")
        return redirect('gym:plan_list')

@login_required
def plan_detail(request, plan_id):
    try:
        plan = get_object_or_404(Plan, id=plan_id, user=request.user)
        plan_devices = plan.plan_devices.all().order_by('order')
        return render(request, 'gym/plans/detail.html', {
            'plan': plan,
            'plan_devices': plan_devices
        })
    except Http404:
        messages.error(request, "The plan you're looking for does not exist or you don't have permission to view it.")
        return redirect('gym:plan_list')
    except Exception as e:
        messages.error(request, f"An error occurred while loading the plan details: {str(e)}")
        return redirect('gym:plan_list')

@login_required
def plan_edit(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id, user=request.user)
    if request.method == 'POST':
        form = PlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, f"Plan '{plan.name}' updated successfully.")
            return redirect('gym:plan_detail', plan_id=plan.id)
    else:
        form = PlanForm(instance=plan)
    return render(request, 'gym/plans/edit.html', {'form': form, 'plan': plan})

@login_required
def plan_delete(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id, user=request.user)
    if request.method == 'POST':
        plan_name = plan.name
        plan.delete()
        messages.success(request, f"Plan '{plan_name}' deleted successfully.")
        return redirect('gym:plan_list')
    return render(request, 'gym/plans/delete.html', {'plan': plan})

@login_required
def plan_add_device(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id, user=request.user)
    
    if request.method == 'POST':
        form = PlanDeviceForm(request.POST)
        if form.is_valid():
            plan_device = form.save(commit=False)
            plan_device.plan = plan
            
            # Determine order (add to end)
            max_order = plan.plan_devices.aggregate(Max('order'))['order__max'] or 0
            plan_device.order = max_order + 1
            
            plan_device.save()
            messages.success(request, "Device added to plan successfully.")
            return redirect('gym:plan_detail', plan_id=plan.id)
    else:
        form = PlanDeviceForm()
        
    # Only show devices created by the user
    form.fields['device'].queryset = Device.objects.filter(created_by=request.user)
    
    return render(request, 'gym/plans/add_device.html', {
        'form': form,
        'plan': plan
    })

@login_required
def plan_remove_device(request, plan_id, plan_device_id):
    plan = get_object_or_404(Plan, id=plan_id, user=request.user)
    plan_device = get_object_or_404(PlanDevice, id=plan_device_id, plan=plan)
    
    if request.method == 'POST':
        # Delete the plan device
        plan_device.delete()
        
        # Reorder remaining devices
        for i, device in enumerate(plan.plan_devices.all().order_by('order')):
            device.order = i + 1
            device.save()
            
        messages.success(request, "Device removed from plan successfully.")
        return redirect('gym:plan_detail', plan_id=plan.id)
    
    return render(request, 'gym/plans/remove_device.html', {
        'plan': plan,
        'plan_device': plan_device
    })

@login_required
def plan_reorder_devices(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id, user=request.user)
    
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Get the new order from the request
        device_order = request.POST.getlist('device_order[]')
        
        # Update the order of each device
        for i, device_id in enumerate(device_order):
            PlanDevice.objects.filter(id=device_id, plan=plan).update(order=i + 1)
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'}, status=400)

# Session views
@login_required
def session_list(request):
    sessions = Session.objects.filter(user=request.user).order_by('-start_time')
    return render(request, 'gym/sessions/list.html', {'sessions': sessions})

@login_required
def session_start(request):
    try:
        # Check if there's already an active session
        active_session = Session.objects.filter(
            user=request.user, 
            status='in_progress'
        ).first()
        
        if active_session:
            messages.warning(request, "You already have an active session.")
            return redirect('gym:session_detail', session_id=active_session.id)
        
        if request.method == 'POST':
            form = SessionStartForm(request.user, request.POST)
            if form.is_valid():
                try:
                    plan = form.cleaned_data['plan']
                    
                    # Create new session
                    session = Session.objects.create(
                        user=request.user,
                        plan=plan,
                        start_time=timezone.now(),
                        status='in_progress'
                    )
                    
                    # Create device sessions for each device in the plan
                    plan_devices = plan.plan_devices.all()
                    if not plan_devices:
                        messages.warning(request, "The selected plan has no devices. Please add devices to your plan.")
                    
                    for plan_device in plan_devices:
                        DeviceSession.create_from_plan_device(session, plan_device)
                    
                    messages.success(request, "Session started successfully.")
                    return redirect('gym:session_detail', session_id=session.id)
                except Exception as e:
                    messages.error(request, f"Error creating session: {str(e)}")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error in {field}: {error}")
        else:
            form = SessionStartForm(request.user)
        
        # Get recent sessions
        recent_sessions = Session.objects.filter(
            user=request.user, 
            status='completed'
        ).order_by('-start_time')[:5]
        
        return render(request, 'gym/sessions/start.html', {
            'form': form,
            'recent_sessions': recent_sessions
        })
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return redirect('gym:index')

@login_required
def session_detail(request, session_id):
    session = get_object_or_404(Session, id=session_id, user=request.user)
    device_sessions = session.device_sessions.all().order_by('order')
    
    return render(request, 'gym/sessions/detail.html', {
        'session': session,
        'device_sessions': device_sessions,
    })

@login_required
def device_session_mark_done(request, session_id, device_session_id):
    try:
        session = get_object_or_404(Session, id=session_id, user=request.user)
        device_session = get_object_or_404(DeviceSession, id=device_session_id, session=session)
        
        if session.status != 'in_progress':
            messages.error(request, "Cannot update a device in a closed session.")
            return redirect('gym:session_detail', session_id=session.id)
        
        if request.method == 'POST':
            # Simply mark the device as performed
            device_session.performed = True
            device_session.save()
            messages.success(request, f"Exercise '{device_session.device.name}' marked as completed.")
        
        return redirect('gym:session_detail', session_id=session.id)
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return redirect('gym:session_detail', session_id=session_id)

@login_required
def device_session_mark_undone(request, session_id, device_session_id):
    try:
        session = get_object_or_404(Session, id=session_id, user=request.user)
        device_session = get_object_or_404(DeviceSession, id=device_session_id, session=session)
        
        if session.status != 'in_progress':
            messages.error(request, "Cannot update a device in a closed session.")
            return redirect('gym:session_detail', session_id=session.id)
        
        if request.method == 'POST':
            # Mark the device as not performed
            device_session.performed = False
            device_session.save()
            messages.success(request, f"Exercise '{device_session.device.name}' marked as not completed.")
        
        return redirect('gym:session_detail', session_id=session.id)
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return redirect('gym:session_detail', session_id=session_id)

@login_required
def device_session_update(request, session_id, device_session_id):
    try:
        session = get_object_or_404(Session, id=session_id, user=request.user)
        device_session = get_object_or_404(DeviceSession, id=device_session_id, session=session)
        
        if session.status != 'in_progress':
            messages.error(request, "Cannot update a device in a closed session.")
            return redirect('gym:session_detail', session_id=session.id)
        
        if request.method == 'POST':
            form = DeviceSessionUpdateForm(request.POST, instance=device_session)
            if form.is_valid():
                try:
                    updated_session = form.save()
                    messages.success(request, f"Exercise '{updated_session.device.name}' updated successfully.")
                    return redirect('gym:session_detail', session_id=session.id)
                except Exception as e:
                    messages.error(request, f"Error saving exercise update: {str(e)}")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error in {field}: {error}")
        else:
            form = DeviceSessionUpdateForm(instance=device_session)
        
        return render(request, 'gym/sessions/device_update.html', {
            'form': form,
            'session': session,
            'device_session': device_session
        })
    except Http404:
        messages.error(request, "The exercise you're trying to update doesn't exist or you don't have permission to update it.")
        return redirect('gym:session_list')
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return redirect('gym:session_list')

@login_required
def session_close(request, session_id):
    session = get_object_or_404(Session, id=session_id, user=request.user)
    
    if session.status != 'in_progress':
        messages.error(request, "Session is already closed.")
        return redirect('gym:session_detail', session_id=session.id)
    
    if request.method == 'POST':
        session.close_session()
        messages.success(request, "Session closed successfully.")
        return redirect('gym:session_list')
    
    return render(request, 'gym/sessions/close.html', {'session': session})

@login_required
def session_cancel(request, session_id):
    session = get_object_or_404(Session, id=session_id, user=request.user)
    
    if session.status != 'in_progress':
        messages.error(request, "Session is already closed.")
        return redirect('gym:session_detail', session_id=session.id)
    
    if request.method == 'POST':
        session.status = 'cancelled'
        session.end_time = timezone.now()
        session.save()
        messages.success(request, "Session cancelled.")
        return redirect('gym:session_list')
    
    return render(request, 'gym/sessions/cancel.html', {'session': session})

# User Profile views
@login_required
def profile_view(request):
    try:
        user = request.user
        # Try to get the profile, or create one if it doesn't exist
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user)
            messages.info(request, "We've created a new profile for you.")
        
        # Get statistics for the user
        total_sessions = Session.objects.filter(user=user).count()
        completed_sessions = Session.objects.filter(user=user, status='completed').count()
        total_plans = Plan.objects.filter(user=user).count()
        total_devices = Device.objects.filter(created_by=user).count()
        
        # Get last 5 sessions
        recent_sessions = Session.objects.filter(user=user).order_by('-start_time')[:5]
        
        context = {
            'user': user,
            'profile': profile,
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'total_plans': total_plans,
            'total_devices': total_devices,
            'recent_sessions': recent_sessions,
        }
        
        return render(request, 'gym/profile/view.html', context)
    except Exception as e:
        messages.error(request, f"An error occurred while loading your profile: {str(e)}")
        return redirect('gym:index')

@login_required
def edit_profile(request):
    try:
        user = request.user
        # Try to get the profile, or create one if it doesn't exist
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user)
            messages.info(request, "We've created a new profile for you.")
        
        if request.method == 'POST':
            form = UserProfileForm(request.POST, instance=profile)
            if form.is_valid():
                form.save(user=user)
                messages.success(request, "Profile updated successfully!")
                return redirect('gym:profile')
            else:
                messages.error(request, "Please correct the errors below.")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error in {field}: {error}")
        else:
            form = UserProfileForm(instance=profile, user=user)
        
        return render(request, 'gym/profile/edit.html', {
            'form': form,
            'user': user,
            'profile': profile,
        })
    except Exception as e:
        messages.error(request, f"An error occurred while updating your profile: {str(e)}")
        return redirect('gym:profile')