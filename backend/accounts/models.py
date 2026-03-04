from django.contrib.auth.models import AbstractUser

# Custom user allows adding fields later (e.g. roles/permissions).
# Passwords are hashed by Django (Argon2) — never stored plaintext.
class User(AbstractUser):
    pass
