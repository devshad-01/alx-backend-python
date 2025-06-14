import logging
from datetime import datetime, timedelta
import os
from django.conf import settings
from django.http import HttpResponseForbidden, JsonResponse
from collections import defaultdict
from django.utils import timezone


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


class OffensiveLanguageMiddleware:
    """
    Middleware to limit the number of chat messages a user can send within a certain time window,
    based on their IP address. Implements rate limiting of 5 messages per minute.
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware with the get_response callable.
        This is called once when the Django app starts.
        """
        self.get_response = get_response
        
        # Dictionary to store message counts per IP address
        # Structure: {ip_address: [(timestamp1, count1), (timestamp2, count2), ...]}
        self.ip_message_tracker = defaultdict(list)
        
        # Rate limiting configuration
        self.max_messages = 5  # Maximum messages allowed
        self.time_window = 60  # Time window in seconds (1 minute)
    
    def get_client_ip(self, request):
        """
        Get the client's IP address from the request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def clean_old_entries(self, ip_address):
        """
        Remove entries older than the time window for a given IP address.
        """
        current_time = timezone.now()
        cutoff_time = current_time - timedelta(seconds=self.time_window)
        
        # Filter out entries older than the time window
        self.ip_message_tracker[ip_address] = [
            entry for entry in self.ip_message_tracker[ip_address]
            if entry[0] > cutoff_time
        ]
    
    def count_recent_messages(self, ip_address):
        """
        Count the number of messages sent by an IP address within the time window.
        """
        self.clean_old_entries(ip_address)
        return len(self.ip_message_tracker[ip_address])
    
    def __call__(self, request):
        """
        Process the request and check if it should be rate limited.
        This is called for each request.
        """
        # Only check POST requests (which are typically used for sending messages)
        if request.method == 'POST':
            # Get client IP address
            client_ip = self.get_client_ip(request)
            
            # Check if this is a message-related endpoint
            # You can customize this condition based on your URL patterns
            if '/messages/' in request.path or '/chats/' in request.path:
                # Count recent messages from this IP
                recent_message_count = self.count_recent_messages(client_ip)
                
                # Check if the limit has been exceeded
                if recent_message_count >= self.max_messages:
                    return JsonResponse({
                        'error': 'Rate limit exceeded',
                        'message': f'You can only send {self.max_messages} messages per minute. Please wait before sending another message.',
                        'retry_after': self.time_window
                    }, status=429)  # 429 Too Many Requests
                
                # If within limit, record this message attempt
                current_time = timezone.now()
                self.ip_message_tracker[client_ip].append((current_time, 1))
        
        # Process the request normally
        response = self.get_response(request)
        return response
