from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # Add additional error handling
    if response is None:
        # Handle unexpected errors
        return Response(
            {
                'error': 'An unexpected error occurred',
                'detail': str(exc)
            }, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Customize error responses
    if response and response.status_code == status.HTTP_400_BAD_REQUEST:
        response.data = {
            'error': 'Validation Error',
            'details': response.data
        }
    
    return response
