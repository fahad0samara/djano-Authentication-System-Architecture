from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
import pyotp

from .models import LoginHistory, FailedLoginAttempt
from .forms import ProfileUpdateForm, TwoFactorSetupForm
from .utils import generate_backup_codes, get_totp_uri, verify_totp

class CustomLoginView(LoginView):
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Record successful login
        LoginHistory.objects.create(
            user=self.request.user,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT'),
            status='success'
        )
        
        # Clear failed attempts
        FailedLoginAttempt.objects.filter(
            username=form.cleaned_data['username']
        ).delete()
        
        return response
    
    def form_invalid(self, form):
        # Record failed attempt
        username = form.cleaned_data.get('username')
        ip = self.request.META.get('REMOTE_ADDR')
        
        attempt, created = FailedLoginAttempt.objects.get_or_create(
            username=username,
            ip_address=ip,
            defaults={'attempt_count': 1}
        )
        
        if not created:
            attempt.attempt_count += 1
            attempt.save()
        
        return super().form_invalid(form)

@login_required
def setup_2fa(request):
    if request.method == 'POST':
        form = TwoFactorSetupForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data['token']
            secret = request.session['2fa_secret']
            
            if verify_totp(secret, token):
                request.user.two_factor_enabled = True
                request.user.backup_codes = generate_backup_codes()
                request.user.save()
                
                messages.success(request, '2FA has been enabled successfully!')
                return redirect('profile')
            else:
                messages.error(request, 'Invalid verification code.')
    else:
        # Generate new secret
        secret = pyotp.random_base32()
        request.session['2fa_secret'] = secret
        qr_uri = get_totp_uri(secret, request.user.username)
        form = TwoFactorSetupForm()
        
    return render(request, 'accounts/setup_2fa.html', {
        'form': form,
        'qr_uri': qr_uri
    })

@login_required
def login_history(request):
    history = LoginHistory.objects.filter(user=request.user)[:20]
    return render(request, 'accounts/login_history.html', {'history': history})