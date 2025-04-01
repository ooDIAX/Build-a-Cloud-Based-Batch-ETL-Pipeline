import os
import json
import functions_framework

@functions_framework.http
def main(request):
    """Simple Hello World function for Cloud Run CI/CD demonstration.
    
    Args:
        request: HTTP request object.
        
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`.
    """
    # Get environment variables (useful for showing configuration in Cloud Run)
    environment = os.environ.get('ENVIRONMENT', 'development')
    
    # Create response data
    response_data = {
        "message": "Hello World!",
        "environment": environment,
        "service": "Cloud Run CI/CD Demo",
        "endpoints": {
            "/": "Returns this welcome message"
        }
    }
    
    # Return JSON response without using Flask
    return (json.dumps(response_data), 200, {'Content-Type': 'application/json'})