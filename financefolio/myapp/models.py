from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, first_name=None, last_name=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name or '',
            last_name=last_name or '',
            **extra_fields
        )
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

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
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

from django.db import models
from django.conf import settings  # To reference the CustomUser model

class Feedback(models.Model):
    RATING_CHOICES = [
        (1, '1 - Very Poor'),
        (2, '2 - Poor'),
        (3, '3 - Average'),
        (4, '4 - Good'),
        (5, '5 - Excellent'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,  # Allows guest users to provide feedback without a user reference
        blank=True,
        related_name='feedbacks'
    )
    feedback_text = models.TextField()
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_display = self.user.email if self.user else "Guest User"
        return f"{user_display} - {self.rating} Stars"

# Optionally, create a view to display feedback for guests and admins.
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

    def total_actual_expenses(self):
        return self.expenses.aggregate(models.Sum('actual_expense'))['actual_expense__sum'] or 0

    def remaining_balance_actual(self):
        if self.actual_income is not None:
            return self.actual_income - self.total_actual_expenses()
        return None

    def __str__(self):
        return f"{self.user.email} - {self.month.strftime('%B %Y')}"


class Expense(models.Model):
    CATEGORIES = [
        ('rent', 'Rent'),
        ('food', 'Food'),
        ('travel', 'Travel'),
        ('entertainment', 'Entertainment'),
        ('electricity', 'Electricity'),
        ('medicine', 'Medicine'),
        ('groceries', 'Groceries'),
        ('bills', 'Bills'),
        ('loan', 'Loan'),
        ('insurance', 'Insurance'),                # Added
        ('transport', 'Transport'),                  # Added
        ('subscriptions', 'Subscriptions'),          # Added
        ('clothing', 'Clothing'),                    # Added
        ('household_supplies', 'Household Supplies'), # Added
        ('dining_out', 'Dining Out'),                # Added
        ('gifts', 'Gifts'),                          # Added
        ('miscellaneous', 'Miscellaneous'),          # Added
        ('charity', 'Charity'),
        ('education', 'Education'),
        ('dress', 'Dress'),
        ('gym', 'Gym'),
        # Option for user-defined category
        ('custom', 'Add Any Other Expense'),
    ]

    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    category = models.CharField(max_length=100, choices=CATEGORIES)
    actual_expense = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"{self.category} - Actual: {self.actual_expense} on {self.date}"


# models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum
from .models import Expense, Budget



class Goal(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='goals'
    )
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, choices=Expense.CATEGORIES)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    deadline = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optional: Link to a specific Budget if needed
    budget = models.ForeignKey(
        Budget,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='goals'
    )

    def __str__(self):
        return f"{self.name} - {self.target_amount} by {self.deadline} ({self.category})"

    def save(self, *args, **kwargs):
        # Sum all expenses for the user's budgets in the selected category
        user_budgets = Budget.objects.filter(user=self.user)
        total_spent = Expense.objects.filter(budget__in=user_budgets, category=self.category).aggregate(Sum('actual_expense'))['actual_expense__sum'] or 0

        # Update current amount with the total expenses for that category
        self.current_amount = total_spent

        # Automatically update status based on current_amount and deadline
        if self.current_amount >= self.target_amount:
            self.status = 'completed'
        elif timezone.now().date() > self.deadline:
            self.status = 'failed'

        # Save the goal
        super().save(*args, **kwargs)


#announcement section#
from django.db import models
from django.conf import settings  # For referencing the CustomUser model

class Announcement(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Optional: allow only admin to create announcements
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='announcements'
    )

    def __str__(self):
        return f"{self.title} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

from django.db import models
from django.conf import settings

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=100, choices=[
        ('tips', 'Tips'),
        ('financial_planning', 'Financial Planning'),
        ('budgeting', 'Budgeting')
    ])
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


from django.db import models
from django.conf import settings

class Query(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('R', 'Resolved'),
        ('C', 'Closed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='queries')
    title = models.CharField(max_length=255)  # Short title for the query
    description = models.TextField()  # Detailed description of the query
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.user.email}"
    
class AdminResponse(models.Model):
    query = models.ForeignKey(Query, on_delete=models.CASCADE, related_name='responses')
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_responses')
    response_text = models.TextField()
    responded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response by {self.admin.email} to {self.query.title}"
