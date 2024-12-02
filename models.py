from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.formats import date_format

class StudentManager(BaseUserManager):
    """
    Personalized manager for Student model, Extends BaseUserManager.
    Documentation BaseUserManager
    https://docs.djangoproject.com/en/5.1/topics/auth/customizing/#django.contrib.auth.models.BaseUserManager
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates the user saving the email and password.
        Args:
            email (str): The student's email.
            password (str, optional): The student's password. Default is None.
            **extra_fields: Additional fields for the Student model.
        Returns:
            Student object
        """
        if password is None:
            raise TypeError('Users must have a password.')
        email = self.normalize_email(email)
        student = self.model(email=email, **extra_fields)
        student.set_password(password)
        student.save(using=self._db)
        return student

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and saves a superuser Student with the given email and password.
        
        Args:
            email (str): The superuser's email.
            password (str, optional): The superuser's password. Default is None.
            **extra_fields: Additional fields for the Student model.
        
        Returns:
            Student: The created and saved superuser Student object.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class Student(AbstractBaseUser, PermissionsMixin):
    """
    Student model that extends AbstractBaseUser and PermissionsMixin.
    AbstractBaseUser docs: https://docs.djangoproject.com/en/5.1/topics/auth/customizing/#django.contrib.auth.models.AbstractBaseUser
    PermissionMixin docs: https://docs.djangoproject.com/en/5.1/topics/auth/customizing/#django.contrib.auth.models.PermissionsMixin
    """
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    lastname1 = models.CharField(max_length=100)
    lastname2 = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    objects = StudentManager()
    last_login = models.DateTimeField(default=timezone.now)
    available_hours = models.IntegerField(default=8)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'lastname1', 'phone']

    def __str__(self):
        """Method that returns the student's full name."""
        return f'{self.name} {self.lastname1} {self.lastname2}'

class Room(models.Model):
    """
    Room model saves the number and the name of the room
    """
    room_number = models.IntegerField()
    name = models.CharField(max_length=100)

    """Method that returns the number and name of the room"""
    def __str__(self):
        return f'{self.room_number} - {self.name}'

class Booking(models.Model):
    """
    Booking model stores information on a room reservation
    """
    user = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)   
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()

    """Method that returns the user, name of the room and the dates"""
    def __str__(self):
        return f'{self.user} ha reservado la {self.room.name} desde {self.check_in} hasta {self.check_out}'