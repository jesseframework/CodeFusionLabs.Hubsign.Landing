"""Response headers Django has no built-in setting for."""


class SecurityHeadersMiddleware:
    """Adds Permissions-Policy to every response.

    Django covers Referrer-Policy, X-Frame-Options, HSTS and nosniff via
    settings, and django-csp covers Content-Security-Policy, but there is no
    built-in for Permissions-Policy. nginx sets it too in production; this
    keeps the header present in local development and in any deployment that
    does not front the app with the bundled nginx config.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        from django.conf import settings
        self.policy = getattr(settings, 'PERMISSIONS_POLICY', '')

    def __call__(self, request):
        response = self.get_response(request)
        if self.policy and 'Permissions-Policy' not in response:
            response['Permissions-Policy'] = self.policy
        return response
