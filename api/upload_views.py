from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.conf import settings
from .utils import success_response, error_response
from .constants import MAX_FILE_SIZE, ALLOWED_IMAGE_TYPES
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Magic bytes for image file types
IMAGE_MAGIC_BYTES = {
    b'\xff\xd8\xff': 'image/jpeg',  # JPEG
    b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a': 'image/png',  # PNG
    b'GIF87a': 'image/gif',  # GIF87a
    b'GIF89a': 'image/gif',  # GIF89a
    b'RIFF': 'image/webp',  # WebP (starts with RIFF)
}


def validate_image_magic_bytes(file):
    """Validate file is actually an image by checking magic bytes"""
    file.seek(0)
    header = file.read(12)
    file.seek(0)
    
    # Check for JPEG
    if header.startswith(b'\xff\xd8\xff'):
        return 'image/jpeg'
    # Check for PNG
    if header.startswith(b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'):
        return 'image/png'
    # Check for GIF
    if header.startswith(b'GIF87a') or header.startswith(b'GIF89a'):
        return 'image/gif'
    # Check for WebP
    if header.startswith(b'RIFF') and b'WEBP' in header:
        return 'image/webp'
    
    return None


from django_ratelimit.decorators import ratelimit

@ratelimit(key='user', rate='20/h', method='POST', block=True)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_file(request):
    """
    Upload file (image) and return public URL
    POST /api/upload/
    """
    if 'file' not in request.FILES:
        return error_response('No file provided')
    
    file = request.FILES['file']
    
    # Validate file size first
    if file.size > MAX_FILE_SIZE:
        return error_response(f'File size exceeds {MAX_FILE_SIZE / (1024 * 1024)}MB limit')
    
    # Validate file type using magic bytes (more secure than content_type)
    detected_type = validate_image_magic_bytes(file)
    
    if not detected_type or detected_type not in ALLOWED_IMAGE_TYPES:
        logger.warning(f"Invalid file type detected: {detected_type}, content_type: {file.content_type}")
        return error_response('Only image files are allowed')
    
    # Also validate content_type as secondary check
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        logger.warning(f"Content type mismatch: {file.content_type} vs detected: {detected_type}")
        return error_response('Invalid file type')
    
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
    
    return success_response({
        'file_url': file_url,
        'file_path': file_path,
        'file_size': file.size,
        'content_type': file.content_type
    }, message='File uploaded successfully')

