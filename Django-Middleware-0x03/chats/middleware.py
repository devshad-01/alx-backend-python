import logging
from datetime import datetime
import os
from django.conf import settings
from django.http import HttpResponseForbidden


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
        self.log_file_path = os.path.join(settings.BASE_DIR, 'requests.log')
        
        # Create a specific logger for this middleware
        self.logger = logging.getLogger('request_logger')
        self.logger.setLevel(logging.INFO)
        
        # Create file handler if it doesn't exist
        if not self.logger.handlers:
            file_handler = logging.FileHandler(self.log_file_path, mode='a')
            file_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

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


class RestrictAccessByTimeMiddleware:
    """
    Middleware to restrict access to the messaging app during certain hours.
    Only allows access between 9 AM and 6 PM.
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware with the get_response callable.
        This is called once when the Django app starts.
        """
        self.get_response = get_response
    
    def __call__(self, request):
        """
        Process the request and check if access is allowed during current time.
        Denies access outside 9 AM - 6 PM hours.
        """
        # Get current hour (24-hour format)
        current_time = datetime.now()
        current_hour = current_time.hour
        
        # Define allowed hours: 9 AM (9) to 6 PM (18)
        start_hour = 9  # 9 AM
        end_hour = 18   # 6 PM
        
        # Check if current time is outside allowed hours
        if current_hour < start_hour or current_hour >= end_hour:
            return HttpResponseForbidden(
                "Access to the messaging app is restricted. "
                "Please access between 9 AM and 6 PM."
            )
        
        # If within allowed hours, proceed with the request
        response = self.get_response(request)
        return response
