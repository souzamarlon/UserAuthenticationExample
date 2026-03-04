"""
Authentication flow over HTTPS:
- Login: verify credentials → issue short-lived access + long-lived refresh.
- Tokens stored in HttpOnly, Secure cookies (no localStorage / XSS).
- Refresh: rotating refresh token; old one invalidated server-side (blacklist).
"""
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .models import User
from .serializers import UserSerializer


def _set_auth_cookies(response, access_token, refresh_token):
    """Set access and refresh as HttpOnly, Secure, SameSite cookies."""
    jwt_settings = getattr(settings, "SIMPLE_JWT", {})
    cookie_kw = {
        "httponly": jwt_settings.get("AUTH_COOKIE_HTTP_ONLY", True),
        "secure": jwt_settings.get("AUTH_COOKIE_SECURE", not settings.DEBUG),
        "samesite": jwt_settings.get("AUTH_COOKIE_SAMESITE", "Lax"),
        "path": jwt_settings.get("AUTH_COOKIE_PATH", "/"),
    }
    access_lifetime = api_settings.ACCESS_TOKEN_LIFETIME
    refresh_lifetime = api_settings.REFRESH_TOKEN_LIFETIME
    response.set_cookie(
        jwt_settings.get("AUTH_COOKIE_ACCESS", "access_token"),
        str(access_token),
        max_age=int(access_lifetime.total_seconds()),
        **cookie_kw,
    )
    response.set_cookie(
        jwt_settings.get("AUTH_COOKIE_REFRESH", "refresh_token"),
        str(refresh_token),
        max_age=int(refresh_lifetime.total_seconds()),
        **cookie_kw,
    )
    return response


def _clear_auth_cookies(response):
    """Clear auth cookies on logout."""
    jwt_settings = getattr(settings, "SIMPLE_JWT", {})
    for name in (
        jwt_settings.get("AUTH_COOKIE_ACCESS", "access_token"),
        jwt_settings.get("AUTH_COOKIE_REFRESH", "refresh_token"),
    ):
        response.delete_cookie(name, path="/")
    return response


@method_decorator(ensure_csrf_cookie, name="get")
class CsrfCookieView(APIView):
    """Ensure CSRF cookie is set so SPA can send X-CSRFToken header."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({}, status=status.HTTP_204_NO_CONTENT)


class LoginView(APIView):
    """Verify credentials over HTTPS; issue JWT access + refresh in HttpOnly cookies."""
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response(
                {"detail": "Username and password required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        from django.contrib.auth import authenticate
        user = authenticate(request, username=username, password=password)
        if not user:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        refresh = RefreshToken.for_user(user)
        response = Response(
            {"user": UserSerializer(user).data},
            status=status.HTTP_200_OK,
        )
        return _set_auth_cookies(response, refresh.access_token, refresh)


class RefreshView(TokenRefreshView):
    """Rotating refresh: read refresh from cookie; issue new access + refresh; blacklist old."""
    permission_classes = [AllowAny]

    def get_refresh_token_from_cookie(self, request):
        jwt_settings = getattr(settings, "SIMPLE_JWT", {})
        return request.COOKIES.get(
            jwt_settings.get("AUTH_COOKIE_REFRESH", "refresh_token")
        )

    def post(self, request, *args, **kwargs):
        refresh_raw = self.get_refresh_token_from_cookie(request)
        if not refresh_raw:
            return Response(
                {"detail": "Refresh token missing."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        request.data.clear()
        request.data["refresh"] = refresh_raw
        try:
            response = super().post(request, *args, **kwargs)
        except (InvalidToken, TokenError):
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if response.status_code != 200:
            return response
        new_access = response.data.get("access")
        new_refresh = response.data.get("refresh")
        if new_access and new_refresh:
            res = Response({"detail": "Refreshed."}, status=status.HTTP_200_OK)
            _set_auth_cookies(res, new_access, new_refresh)
            return res
        return response


class LogoutView(APIView):
    """Blacklist current refresh token and clear auth cookies."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        jwt_settings = getattr(settings, "SIMPLE_JWT", {})
        refresh_raw = request.COOKIES.get(
            jwt_settings.get("AUTH_COOKIE_REFRESH", "refresh_token")
        )
        if refresh_raw:
            try:
                token = RefreshToken(refresh_raw)
                token.blacklist()
            except (InvalidToken, TokenError):
                pass
        response = Response({"detail": "Logged out."}, status=status.HTTP_200_OK)
        return _clear_auth_cookies(response)


class MeView(APIView):
    """Validate session: return current user from JWT (signature + expiration + claims)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"user": UserSerializer(request.user).data})
