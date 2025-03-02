from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

class EmailService:
    @staticmethod
    def send_login_alert(user, ip_address: str, user_agent: str) -> None:
        """Send email alert for new login from unknown device."""
        context = {
            'username': user.username,
            'ip_address': ip_address,
            'user_agent': user_agent
        }
        
        message = render_to_string('accounts/emails/login_alert.html', context)
        
        send_mail(
            subject='New Login Detected',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=message
        )
    
    @staticmethod
    def send_2fa_disabled_alert(user) -> None:
        """Send alert when 2FA is disabled."""
        message = render_to_string('accounts/emails/2fa_disabled.html', {
            'username': user.username
        })
        
        send_mail(
            subject='2FA Has Been Disabled',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=message
        )