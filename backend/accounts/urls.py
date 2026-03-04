from django.urls import path
from .views import CsrfCookieView, LoginView, RefreshView, LogoutView, MeView

urlpatterns = [
    path("csrf/", CsrfCookieView.as_view(), name="auth_csrf"),
    path("login/", LoginView.as_view(), name="auth_login"),
    path("refresh/", RefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="auth_logout"),
    path("me/", MeView.as_view(), name="auth_me"),
]
