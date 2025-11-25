"""
WSGI config for orm_cashback project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import signal
import sys
import logging

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orm_cashback.settings')

logger = logging.getLogger(__name__)

# Graceful shutdown handler
def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    # Close database connections
    from django.db import connections
    for conn in connections.all():
        conn.close()
    logger.info("Graceful shutdown completed")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

application = get_wsgi_application()
