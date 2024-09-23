from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, gender=None, age=None, address=None, city=None, state=None):
        if not email:
            raise ValueError('The Email field must be set')
        if not first_name:
            raise ValueError('The First Name field must be set')
        if not last_name:
            raise ValueError('The Last Name field must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, gender=gender, age=age, address=address, city=city, state=state)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, gender=None, age=None, address=None, city=None, state=None):
        user = self.create_user(email, first_name, last_name, password, gender, age, address, city, state)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True
#............................................................#
from django.db import models
from django.conf import settings  # To reference the CustomUser model

class Budget(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='budgets'
    )
    month = models.DateField()
    planned_income = models.DecimalField(max_digits=12, decimal_places=2)
    actual_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def total_planned_expenses(self):
        return self.expenses.aggregate(models.Sum('planned_expense'))['planned_expense__sum'] or 0

    def total_actual_expenses(self):
        return self.expenses.aggregate(models.Sum('actual_expense'))['actual_expense__sum'] or 0

    def remaining_balance_planned(self):
        return self.planned_income - self.total_planned_expenses()

    def remaining_balance_actual(self):
        if self.actual_income is not None:
            return self.actual_income - self.total_actual_expenses()
        return None

    def __str__(self):
        return f"{self.user.email} - {self.month.strftime('%B %Y')}"

class Expense(models.Model):
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    category = models.CharField(max_length=100)
    planned_expense = models.DecimalField(max_digits=12, decimal_places=2)
    actual_expense = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.category} - Planned: {self.planned_expense}, Actual: {self.actual_expense}"
