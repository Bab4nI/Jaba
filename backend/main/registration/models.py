from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    group = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    department = models.CharField(max_length=100, null=False, default="")
    level = models.CharField(max_length=100, null=False, default="")
    course = models.CharField(max_length=100, null=False, default="")

    def set_password(self, raw_password):
        """
        Хеширует пароль и сохраняет его в поле password.
        """
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """
        Проверяет, совпадает ли переданный пароль с хешированным паролем в базе данных.
        """
        return check_password(raw_password, self.password)
    
    @staticmethod
    def create_user(**kwargs):
        """
        Создает пользователя с хэшированным паролем.
        """
        password = kwargs.pop('password', None)
        user = User(**kwargs)
        if password:
            user.password = make_password(password)
        user.save()
        return user
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"