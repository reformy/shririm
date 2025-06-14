from django import forms
from django.contrib.auth.models import User
from .models import Device, Plan, PlanDevice, Session, DeviceSession, UserProfile

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class PlanDeviceForm(forms.ModelForm):
    class Meta:
        model = PlanDevice
        fields = ['device', 'name', 'chair_position', 'weight', 'sets', 'moves_per_set']
        widgets = {
            'device': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'chair_position': forms.TextInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.25'}),
            'sets': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'moves_per_set': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make name field optional in the form - model will auto-generate if not provided
        self.fields['name'].required = False
        
        # If we're editing an existing object, show its current name
        if self.instance and self.instance.pk:
            self.fields['name'].initial = self.instance.name

class SessionStartForm(forms.Form):
    plan = forms.ModelChoiceField(
        queryset=Plan.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, user, *args, **kwargs):
        super(SessionStartForm, self).__init__(*args, **kwargs)
        self.fields['plan'].queryset = Plan.objects.filter(user=user)

class DeviceSessionUpdateForm(forms.ModelForm):
    class Meta:
        model = DeviceSession
        fields = ['chair_position', 'weight', 'sets', 'moves_per_set', 'performed', 'notes']
        widgets = {
            'chair_position': forms.TextInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.25'}),
            'sets': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'moves_per_set': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'performed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = UserProfile
        fields = ['bio', 'date_of_birth', 'weight', 'height', 'goal', 'timezone']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'goal': forms.TextInput(attrs={'class': 'form-control'}),
            'timezone': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        """Initialize the form with user data"""
        user = kwargs.pop('user', None)
        super(UserProfileForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
    
    def save(self, user=None, commit=True):
        """Save both the user and profile data"""
        profile = super(UserProfileForm, self).save(commit=False)
        
        if user:
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            
            if commit:
                user.save()
                profile.save()
                
        return profile