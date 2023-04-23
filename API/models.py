import jwt

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import (
	AbstractBaseUser, BaseUserManager, PermissionsMixin
)

from django.db import models
from multiselectfield import MultiSelectField

from django.contrib.postgres.fields import ArrayField

class UserManager(BaseUserManager):
    def create_user(self, password=None, **kwargs):

        if kwargs["email"] is None:
            raise TypeError('Users must have an email address.')
        user = self.model(**kwargs)

        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(db_index=True, unique=True)

    role = models.CharField(max_length=20, null=True)
    name = models.CharField(max_length=30, null=True)
    image = models.TextField(null=True)
    sex = models.CharField(max_length=10, null=True)
    birth_date = models.DateField(null=True)
    phone_number = models.CharField(max_length=12, null=True)
    about_self = models.TextField(max_length=300, null=True)

    learning_trajectory = models.CharField(max_length=50, null=True)
    course_number = models.IntegerField(null=True)
    education_stage = models.CharField(max_length=30, null=True)


    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        """ Строковое представление модели (отображается в консоли) """
        return self.email

    @property
    def token(self):
        """
        Позволяет получить токен пользователя путем вызова user.token, вместо
        user._generate_jwt_token(). Декоратор @property выше делает это
        возможным. token называется "динамическим свойством".
        """
        return self._generate_jwt_token()


    def _generate_jwt_token(self):
        """
        Генерирует веб-токен JSON, в котором хранится идентификатор этого
        пользователя, срок действия токена составляет 1 день от создания
        """
        dt = datetime.now() + timedelta(days=1)

        token = jwt.encode({
            'id': self.pk,
            'exp': dt.utcfromtimestamp(dt.timestamp())
        }, settings.SECRET_KEY, algorithm='HS256')

        return token


class Competence(models.Model):

    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class User_competence(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    competence_id = models.ForeignKey(Competence, on_delete=models.CASCADE)

class Trajectory(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name