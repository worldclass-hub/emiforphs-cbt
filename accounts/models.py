from django.contrib.auth.models import AbstractUser
from django.db import models

class Role(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    TEACHER = 'TEACHER', 'Teacher'
    STUDENT = 'STUDENT', 'Student'

class CustomUser(AbstractUser):
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    phone = models.CharField(max_length=15, blank=True, null=True)
    school_name = models.CharField(max_length=200, blank=True, null=True)
    
    def is_teacher(self):
        return self.role == Role.TEACHER
    
    def is_student(self):
        return self.role == Role.STUDENT
    
    def is_admin_user(self):
        return self.role == Role.ADMIN or self.is_superuser
    
    def get_full_name(self):
        """Return the full name of the user"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name} ({self.username})"
        return f"{self.username} ({self.role})"