"""
Shared utilities and helper functions
"""
from rest_framework.response import Response
from rest_framework import status
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class StandardResultsSetPagination:
    """Standard pagination class for API responses"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


def success_response(
    data: Optional[Dict[str, Any]] = None,
    message: str = 'Success',
    status_code: int = status.HTTP_200_OK
) -> Response:
    """
    Create a standardized success response
    
    Args:
        data: Response data dictionary
        message: Success message
        status_code: HTTP status code
        
    Returns:
        Response: Standardized success response
    """
    response_data = {
        'status': 'success',
        'message': message
    }
    if data:
        response_data.update(data)
    
    return Response(response_data, status=status_code)


def error_response(
    message: str,
    errors: Optional[Dict[str, Any]] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST
) -> Response:
    """
    Create a standardized error response
    
    Args:
        message: Error message (generic, no internal details)
        errors: Optional field-specific errors dictionary
        status_code: HTTP status code
        
    Returns:
        Response: Standardized error response
    """
    response_data = {
        'status': 'error',
        'message': message
    }
    if errors:
        response_data['errors'] = errors
    
    return Response(response_data, status=status_code)


def unauthorized_response(message: str = 'Authentication required') -> Response:
    """Create standardized unauthorized response"""
    return error_response(message, status_code=status.HTTP_401_UNAUTHORIZED)


def forbidden_response(message: str = 'Permission denied') -> Response:
    """Create standardized forbidden response"""
    return error_response(message, status_code=status.HTTP_403_FORBIDDEN)


def not_found_response(message: str = 'Resource not found') -> Response:
    """Create standardized not found response"""
    return error_response(message, status_code=status.HTTP_404_NOT_FOUND)


def server_error_response(message: str = 'Internal server error') -> Response:
    """Create standardized server error response"""
    return error_response(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

