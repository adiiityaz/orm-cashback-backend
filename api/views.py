from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.db import connection
from .utils import success_response, server_error_response
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint with database connectivity check
    
    GET /api/health/
    
    Returns:
        Response: Health status with database connectivity check
    """
    try:
        # Check database connectivity
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = 'connected'
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = 'disconnected'
    
    health_data = {
        'message': 'ORM Cashback API is running',
        'version': '1.0.0',
        'database': db_status
    }
    
    if db_status == 'disconnected':
        return server_error_response('Database connection failed')
    
    return success_response(health_data)
