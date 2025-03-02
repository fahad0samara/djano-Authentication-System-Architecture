from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import LoginHistory
from .serializers import LoginHistorySerializer

class LoginHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LoginHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return LoginHistory.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def recent(self):
        """Get recent login history."""
        queryset = self.get_queryset()[:5]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)