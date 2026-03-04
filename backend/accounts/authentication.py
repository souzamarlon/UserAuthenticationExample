"""
Authorization middleware: validate token signature, expiration, and claims (user id).
Reads JWT from HttpOnly cookie first, then falls back to Authorization header.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.settings import api_settings
from django.conf import settings


class JWTCookieAuthentication(JWTAuthentication):
    """Authenticate using JWT from cookie (access_token) or Authorization header."""

    def authenticate(self, request):
        cookie_name = getattr(
            api_settings,
            "AUTH_COOKIE_ACCESS",
            getattr(settings, "SIMPLE_JWT", {}).get("AUTH_COOKIE_ACCESS", "access_token"),
        )
        raw_token = request.COOKIES.get(cookie_name)
        if not raw_token:
            return super().authenticate(request)
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
