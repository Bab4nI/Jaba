from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import secrets
from django.contrib.auth.hashers import make_password

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        
        return self.create_user(email, password, **extra_fields)
    
    def generate_reset_code(self):
        """Генерирует случайный код для сброса пароля"""
        return secrets.token_urlsafe(32)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, default="")
    group = models.CharField(max_length=100, blank=True, default="")
    is_active = models.BooleanField(default=True)
    new_email = models.EmailField(blank=True, null=True)
    email_verification_code = models.CharField(max_length=6, blank=True, null=True)
    email_verification_code_expires = models.DateTimeField(null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
    
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('student', 'Student'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    avatar_base64 = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.middle_name}"

    def save(self, *args, **kwargs):
        self.role = 'admin' if self.is_staff else 'student'
        super().save(*args, **kwargs)