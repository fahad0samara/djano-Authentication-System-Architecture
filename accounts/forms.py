from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username', 'email', 'bio', 'profile_picture',
            'location', 'timezone', 'github_url', 'linkedin_url', 'twitter_url'
        ]
        
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

class TwoFactorSetupForm(forms.Form):
    token = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={'placeholder': 'Enter 6-digit code'})
    )