import sys
import os
import json

# Add the parent directory to the path so we can import the main app
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import the main Flask app
from app import app

# Netlify function handler
def handler(event, context):
    import io
    from werkzeug.datastructures import Headers
    from werkzeug.wrappers import Response
    
    # Extract request information from the event
    path = event.get('path', '/')
    http_method = event.get('httpMethod', 'GET')
    headers = event.get('headers', {})
    query_string = event.get('queryStringParameters', {})
    body = event.get('body', '')
    is_base64_encoded = event.get('isBase64Encoded', False)
    
    # Create a WSGI environment
    environ = {
        'REQUEST_METHOD': http_method,
        'PATH_INFO': path,
        'QUERY_STRING': '&'.join([f"{k}={v}" for k, v in query_string.items()]) if query_string else '',
        'CONTENT_TYPE': headers.get('content-type', ''),
        'CONTENT_LENGTH': str(len(body)) if body else '',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '80',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'http',
        'wsgi.input': io.BytesIO(body.encode() if body else b''),
        'wsgi.errors': sys.stderr,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
        'wsgi.multithread': False,
    }
    
    # Add headers to environ
    for key, value in headers.items():
        environ[f'HTTP_{key.upper().replace("-", "_")}'] = value
    
    # Create a response
    response = Response.from_app(app, environ)
    
    # Prepare the response for Netlify
    response_dict = {
        'statusCode': response.status_code,
        'headers': dict(response.headers),
        'body': response.get_data(as_text=True)
    }
    
    return response_dict