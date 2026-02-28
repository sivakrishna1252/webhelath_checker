"""
Forms for the monitoring application.
"""
from django import forms
from .models import Website, InternalApp


class WebsiteForm(forms.ModelForm):
    """Form for creating and editing websites."""
    
    class Meta:
        model = Website
        fields = [
            'name', 'url', 'description', 'status', 'check_interval',
            'timeout', 'expected_status_code', 'send_recovery_email',
            'alert_email', 'recovery_email'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'check_interval': forms.NumberInput(attrs={'class': 'form-control'}),
            'timeout': forms.NumberInput(attrs={'class': 'form-control'}),
            'expected_status_code': forms.NumberInput(attrs={'class': 'form-control'}),
            'send_recovery_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'alert_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'recovery_email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['recovery_email'].required = False
        self.fields['description'].required = False
        
        # Add help text
        self.fields['check_interval'].help_text = 'Check interval in seconds (default: 300 = 5 minutes)'
        self.fields['timeout'].help_text = 'Request timeout in seconds (default: 30)'
        self.fields['expected_status_code'].help_text = 'Expected HTTP status code (default: 200)'
        self.fields['recovery_email'].help_text = 'Leave blank to use the same as alert email'


class InternalAppForm(forms.ModelForm):
    """Form for creating and editing internal apps."""
    
    class Meta:
        model = InternalApp
        fields = [
            'name', 'app_type', 'url', 'description', 'is_active',
            'expected_status_code', 'timeout'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'app_type': forms.Select(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'expected_status_code': forms.NumberInput(attrs={'class': 'form-control'}),
            'timeout': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
        
        # Add help text
        self.fields['expected_status_code'].help_text = 'Expected HTTP status code (default: 200)'
        self.fields['timeout'].help_text = 'Request timeout in seconds (default: 30)'
