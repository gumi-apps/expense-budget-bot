from typing import Any
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    def create(self, **kwargs: Any) -> Any:
        return super().create(**kwargs)

    def create_superuser(self, **kwargs):
        user = self.create(**kwargs)
        user.is_staff = True
        user.is_superuser = True

        user.save()

        return user


class User(AbstractUser):
    phone_number = models.CharField()
    chat_id = models.BigIntegerField(unique=True, null=True, blank=True)
    last_name = models.CharField(null=True, blank=True)


# class Expense(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="expenses")
#     amount = models.PositiveIntegerField()
#     reason = models.CharField(max_length=255)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)


class Debt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="debts")
    amount = models.IntegerField()
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="incomes")
    amount = models.IntegerField()
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.reason}: {self.amount}"


class Streak(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="streaks")
    amount = models.PositiveIntegerField()
    current = models.PositiveIntegerField()
    deadline = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
