import logging
import time

logger = logging.getLogger(__name__)

class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log request details
        start_time = time.time()
        
        response = self.get_response(request)
        
        # Calculate request processing time
        duration = time.time() - start_time
        
        logger.info(
            f"Method: {request.method}, "
            f"Path: {request.path}, "
            f"Status: {response.status_code}, "
            f"Duration: {duration:.2f}s"
        )
        
        return response
