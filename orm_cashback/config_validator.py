"""
Environment variable validation on startup
"""
import os
import logging

logger = logging.getLogger(__name__)


def validate_environment_variables():
    """
    Validate required environment variables on startup
    
    Raises:
        ValueError: If required variables are missing in production
    """
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    
    required_vars = {
        'SECRET_KEY': 'Django secret key for cryptographic signing',
        'DB_NAME': 'PostgreSQL database name',
        'DB_USER': 'PostgreSQL database user',
        'DB_PASSWORD': 'PostgreSQL database password',
    }
    
    missing_vars = []
    for var_name, description in required_vars.items():
        if not os.getenv(var_name) and not DEBUG:
            missing_vars.append(f"{var_name} ({description})")
    
    if missing_vars:
        error_msg = f"Missing required environment variables in production:\n" + "\n".join(f"  - {var}" for var in missing_vars)
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Warn about optional but recommended variables
    optional_vars = {
        'RAZORPAY_KEY_ID': 'Razorpay payment gateway key',
        'RAZORPAY_KEY_SECRET': 'Razorpay payment gateway secret',
        'RAZORPAY_WEBHOOK_SECRET': 'Razorpay webhook signature secret',
        'AWS_ACCESS_KEY_ID': 'AWS S3 access key (for file storage)',
        'AWS_SECRET_ACCESS_KEY': 'AWS S3 secret key',
    }
    
    missing_optional = []
    for var_name, description in optional_vars.items():
        if not os.getenv(var_name):
            missing_optional.append(f"{var_name} ({description})")
    
    if missing_optional:
        logger.warning(f"Optional environment variables not set (features may be limited):\n" + "\n".join(f"  - {var}" for var in missing_optional))
    
    logger.info("Environment variable validation completed")

