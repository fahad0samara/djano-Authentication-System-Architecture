from rest_framework import serializers
from ..models import LoginHistory

class LoginHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginHistory
        fields = ['timestamp', 'ip_address', 'user_agent', 'status']
        read_only_fields = fields