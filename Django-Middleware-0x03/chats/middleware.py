import logging
from datetime import datetime
import os
from django.conf import settings


class RequestLoggingMiddleware:
    """
    Middleware to log user requests with timestamp, user, and request path.
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware with the get_response callable.
        This is called once when the Django app starts.
        """
        self.get_response = get_response
        
        # Set up logging configuration
        log_file_path = os.path.join(settings.BASE_DIR, 'requests.log')
        
        # Configure logging
        logging.basicConfig(
            filename=log_file_path,
            level=logging.INFO,
            format='%(message)s',
            filemode='a'  # Append mode
        )
        
        self.logger = logging.getLogger('request_logger')

    def __call__(self, request):
        """
        Process the request and log the required information.
        This is called for each request.
        """
        # Get user information
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous'
        
        # Log the request information
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        self.logger.info(log_message)
        
        # Call the next middleware or view
        response = self.get_response(request)
        
        return response
