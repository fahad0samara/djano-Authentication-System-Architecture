from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

class NotificationService:
    @staticmethod
    def send_security_alert(user, alert_type: str, context: dict) -> None:
        """Send security-related notifications."""
        templates = {
            'suspicious_login': 'accounts/emails/suspicious_login.html',
            'password_changed': 'accounts/emails/password_changed.html',
            'account_locked': 'accounts/emails/account_locked.html'
        }
        
        template = templates.get(alert_type)
        if not template:
            return
            
        message = render_to_string(template, context)
        
        send_mail(
            subject=f'Security Alert: {alert_type}',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=message
        )