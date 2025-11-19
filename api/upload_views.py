from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.conf import settings
import os
from datetime import datetime


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_file(request):
    """
    Upload file (image) and return public URL
    POST /api/upload/
    """
    if 'file' not in request.FILES:
        return Response({
            'status': 'error',
            'message': 'No file provided'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    
    # Validate file type (images only)
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        return Response({
            'status': 'error',
            'message': 'Only image files are allowed'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate file size (max 10MB)
    if file.size > 10 * 1024 * 1024:
        return Response({
            'status': 'error',
            'message': 'File size exceeds 10MB limit'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Generate unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_extension = os.path.splitext(file.name)[1]
    filename = f"uploads/{timestamp}_{file.name}"
    
    # Save file
    file_path = default_storage.save(filename, file)
    
    # Get file URL
    if settings.DEBUG:
        file_url = f"{settings.MEDIA_URL}{file_path}"
    else:
        # In production, this would be S3 URL
        # file_url = f"https://{settings.AWS_S3_BUCKET_NAME}.s3.amazonaws.com/{file_path}"
        file_url = f"{settings.MEDIA_URL}{file_path}"
    
    return Response({
        'status': 'success',
        'message': 'File uploaded successfully',
        'file_url': file_url,
        'file_path': file_path,
        'file_size': file.size,
        'content_type': file.content_type
    }, status=status.HTTP_200_OK)

