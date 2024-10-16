from django.utils.deprecation import MiddlewareMixin

class NoCacheMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'  # For HTTP 1.0
        response['Expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'  # Past date
        return response
