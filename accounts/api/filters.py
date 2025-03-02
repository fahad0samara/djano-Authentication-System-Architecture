from django_filters import rest_framework as filters
from accounts.models import LoginHistory, UserActivity

class LoginHistoryFilter(filters.FilterSet):
    start_date = filters.DateTimeFilter(field_name="timestamp", lookup_expr="gte")
    end_date = filters.DateTimeFilter(field_name="timestamp", lookup_expr="lte")
    status = filters.CharFilter(field_name="status")
    
    class Meta:
        model = LoginHistory
        fields = ['status', 'ip_address']

class UserActivityFilter(filters.FilterSet):
    start_date = filters.DateTimeFilter(field_name="timestamp", lookup_expr="gte")
    end_date = filters.DateTimeFilter(field_name="timestamp", lookup_expr="lte")
    action = filters.CharFilter(field_name="action")
    
    class Meta:
        model = UserActivity
        fields = ['action', 'ip_address']