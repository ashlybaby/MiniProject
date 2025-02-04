from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm as BaseUserChangeForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from .models import Query
from .models import Article
from django.contrib.auth import authenticate

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password", min_length=6)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Birth Date")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'gender', 'address', 'city', 'state', 'birth_date', 'password', 'confirm_password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("This email address is already registered."))
        return email

    def clean(self):
        cleaned_data = super().clean()
        missing_fields = []

        # Check for required fields
        required_fields = ['first_name', 'last_name', 'email', 'gender', 'address', 'city', 'state', 'birth_date', 'password', 'confirm_password']
        for field in required_fields:
            if not cleaned_data.get(field):
                missing_fields.append(field)

        if missing_fields:
            raise ValidationError(_("The following fields are required: {}").format(", ".join(missing_fields)))

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and len(password) < 6:
            raise ValidationError(_("Password must be at least 6 characters long."))
        
        if password != confirm_password:
            raise ValidationError(_("Passwords do not match."))
        
       

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

            if birth_date > today:
                raise ValidationError(_("Birth date cannot be in the future."))
            if age < 18:
                raise ValidationError(_("You must be at least 18 years old to register."))
            if age > 100:
                raise ValidationError(_("You have crossed the age limit."))
        return birth_date

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password'])  # Hash the password
        user.age = self.calculate_age(user.birth_date)  # Calculate age based on birth date
        if commit:
            user.save()
        return user

    def calculate_age(self, birth_date):
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age

class UserChangeForm(BaseUserChangeForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'gender', 'address', 'city', 'state', 'is_active', 'is_staff']


class UserChangeForm(BaseUserChangeForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'gender', 'address', 'city', 'state', 'is_active', 'is_staff']




class UserLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'id': 'emailid', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'id': 'passwords', 'placeholder': 'Password'}))
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            try:
                # Try to get the user from the database
                user = User.objects.get(email=email)

                # Check if the user is active
                if not user.is_active:
                    raise forms.ValidationError(
                        'Your account has been deactivated. Please contact support at financefolio2024@gmail.com.'
                    )

                # Authenticate the user (checks password)
                user = authenticate(email=email, password=password)
                if user is None:
                    raise forms.ValidationError('Invalid email or password')
                    
            except User.DoesNotExist:
                # User not registered
                raise forms.ValidationError('You are not registered. Please sign up.')

        return cleaned_data




from django.contrib.auth import authenticate
  # Replace with the path to your custom User model

class AdminLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            try:
                # Try to get the user from the database
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise forms.ValidationError('You are not registered. Please sign up.')

            # Authenticate the user (check password)
            user = authenticate(email=email, password=password)
            if user is None:
                raise forms.ValidationError('Invalid email or password')
            if not user.is_active:
                raise forms.ValidationError('Your account is disabled.')
            if not user.is_superuser:
                raise forms.ValidationError('You are not permitted to access this section.')

        return cleaned_data
    
    # forms.py
from django import forms

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label='Enter your email address')



from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordResetForm


User = get_user_model()

class CustomPasswordResetForm(PasswordResetForm):

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            self.add_error('email', "There is no user registered with the specified email address.")
        return email

    def save(self, *args, **kwargs):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            return self.cleaned_data
        return super().save(*args, **kwargs)



from django.contrib.auth.forms import SetPasswordForm


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New password'}),
        strip=False,
        min_length=6  # Minimum length requirement
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'}),
        strip=False,
        min_length=6  # Minimum length requirement
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        # Check if both passwords are provided and match
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise ValidationError("Passwords do not match.")

        # Check for minimum length of 6 characters
        if new_password1 and len(new_password1) < 6:
            raise ValidationError("Password must be at least 6 characters long.")

        return cleaned_data



# forms.py

#from django import forms
#from django.contrib.auth.forms import UserChangeForm
#from .models import User

#class CustomUserChangeForm(UserChangeForm):
    #class Meta:
        #model = User
        #fields = ['first_name', 'last_name', 'email', 'gender', 'age', 'address', 'city', 'state']
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserChangeForm
from .models import User

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'gender', 'age', 'address', 'city', 'state']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the password fields
        self.fields.pop('password')
        self.fields.pop('password2', None)

    # Validation for first_name
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name.isalpha():  # Ensure the name only contains letters
            raise ValidationError('First name should contain only letters.')
        return first_name

    # Validation for last_name
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name.isalpha():
            raise ValidationError('Last name should contain only letters.')
        return last_name

    # Validation for email
    def clean_email(self):
        # Since the field is disabled, ensure it's not being altered
        # Fetch the original email from the instance
        original_email = self.instance.email
        current_email = self.cleaned_data.get('email')
        if current_email != original_email:
            raise ValidationError("You cannot change your email address.")
        return original_email

    # Validation for gender
    def clean_gender(self):
     gender = self.cleaned_data.get('gender')
     if not gender:  # Check if gender is empty
        raise ValidationError('Gender is a mandatory field. Please select a gender.')
     return gender
    # Validation for age
    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age <= 18 or age > 100:  # Ensure age is within a realistic range
            raise ValidationError('Age should be between 18 and 100.')
        return age

    # Validation for address
    def clean_address(self):
        address = self.cleaned_data.get('address')
        if address and address.isalpha():
            return address
        else:
            raise ValidationError('City should contain only letters.')
       

    # Validation for city
    def clean_city(self):
        city = self.cleaned_data.get('city')
        if city and city.isalpha():
            return city
        else:
            raise ValidationError('City should contain only letters.')
       

    # Validation for state
    def clean_state(self):
        state = self.cleaned_data.get('state')
        if state and state.isalpha():
            return state
        else:
            raise ValidationError('State should contain only letters.')
      


#........................................................................................................#
from django import forms
from .models import Budget, Expense
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.core.validators import MinValueValidator

def validate_positive(value):
    if value < 0:
        raise forms.ValidationError("Value must be positive.")

class BudgetForm(forms.ModelForm):
    month = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'month'}),
        input_formats=['%Y-%m']  # Accepts YYYY-MM format
    )
    planned_income = forms.DecimalField(
        validators=[validate_positive],
        decimal_places=2,
        max_digits=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter planned income',
        })
    )

    class Meta:
        model = Budget
        fields = ['month', 'planned_income']

    def clean(self):
        cleaned_data = super().clean()
        planned_income = cleaned_data.get('planned_income')

        if planned_income is not None and planned_income < Decimal('0.00'):
            self.add_error('planned_income', "Planned income cannot be negative.")

    

          

    def fill_existing_budget(self, month):
        """ Autofill form fields with existing budget data for a given month. """
        try:
            existing_budget = Budget.objects.get(month=month)
            self.fields['planned_income'].initial = existing_budget.planned_income
            # Add any additional fields you want to autofill
        except Budget.DoesNotExist:
            pass  # No existing budget for this month
# forms.py


from decimal import Decimal
from django import forms
from .models import Expense, Budget

def validate_positive(value):
    if value < 0:
        raise forms.ValidationError("Value must be positive.")

class ExpenseForm(forms.ModelForm):
    custom_category = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter custom category',
        })
    )

    actual_expense = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        validators=[validate_positive],  # Ensure that expense is positive
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter amount',
            'min': '0',
        })
    )

    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        }),
        input_formats=['%Y-%m-%d']
    )

    class Meta:
        model = Expense
        fields = ['budget', 'category', 'custom_category', 'actual_expense', 'date']
        widgets = {
            'budget': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control', 'id': 'category-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['budget'].queryset = Budget.objects.all()
        self.fields['category'].choices = Expense.CATEGORIES

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        custom_category = cleaned_data.get('custom_category')
        actual_expense = cleaned_data.get('actual_expense')
        date = cleaned_data.get('date')

        # Ensure at least one of actual_expense or custom_category is provided for new entries
        if not self.instance.pk:  # Only check for new entries
            if not actual_expense and not custom_category:
                self.add_error(None, "At least one expense entry (actual expense or custom category) is required.")

        # Allow editing with empty fields
        if self.instance.pk:  # Check if an instance of Expense is being edited
            if not actual_expense and not custom_category:  # Both can be empty during editing
                return cleaned_data  # Skip further validation

        # Custom category validation
        if category == 'custom' and not custom_category:
            self.add_error('custom_category', "Please provide a custom category.")

        # Actual expense validation
        if category and not actual_expense:
            self.add_error('actual_expense', "Please provide an expense amount.")

        budget = cleaned_data.get('budget')
        if budget and date:
            if not (budget.month.year == date.year and budget.month.month == date.month):
                self.add_error('date', "Expense date must be within the selected budget month.")

        from datetime import date as date_today
        if date and date > date_today.today():
            self.add_error('date', "Expense date cannot be in the future.")

        return cleaned_data

    def clean_actual_expense(self):
        actual_expense = self.cleaned_data.get('actual_expense')
        if actual_expense is not None and actual_expense <= 0:
            raise forms.ValidationError("Expense must be greater than zero.")
        return actual_expense



#...............................................................................................#
#feedback
from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feedback_text', 'rating']

    feedback_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 50}),
        label='Your Feedback',
        max_length=1000,
        help_text="Please provide your feedback (max 1000 characters)."
    )
    
    # Remove the redefinition of the rating field here
    # rating = forms.ChoiceField(choices=Feedback.RATING_CHOICES, ...)

    def clean_feedback_text(self):
        feedback_text = self.cleaned_data.get('feedback_text')
        if len(feedback_text.strip()) < 3:
            raise forms.ValidationError('Feedback must be at least 3 characters long.')
        return feedback_text
   
    def clean(self):
        cleaned_data = super().clean()
        rating = cleaned_data.get('rating')

        # Validate that a rating is provided
        if not rating:
            raise forms.ValidationError('Please rate us before submitting.')

        return cleaned_data
    

#Goal Section#
from django import forms
from .models import Goal

# Define your categories here
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
    ('insurance', 'Insurance'),
    ('transport', 'Transport'),
    ('subscriptions', 'Subscriptions'),
    ('clothing', 'Clothing'),
    ('household_supplies', 'Household Supplies'),
    ('dining_out', 'Dining Out'),
    ('gifts', 'Gifts'),
    ('miscellaneous', 'Miscellaneous'),
    ('charity', 'Charity'),
    ('education', 'Education'),
    ('dress', 'Dress'),
    ('gym', 'Gym'),
    ('custom', 'Add Any Other Expense'),
]

from django import forms
from django.utils import timezone
from .models import Goal

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['name', 'category', 'target_amount', 'deadline']

    # Ensure target amount is positive
    def clean_target_amount(self):
        target_amount = self.cleaned_data.get('target_amount')
        if target_amount <= 0:
            raise forms.ValidationError("Target amount must be greater than 0.")
        return target_amount

    # Ensure deadline is in the future
    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if deadline <= timezone.now().date():
            raise forms.ValidationError("Deadline must be a future date.")
        return deadline



from .models import Announcement
import re

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'message']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise forms.ValidationError("Title is required.")
        if len(title) < 5:
            raise forms.ValidationError("Title must be at least 5 characters long.")
        if not re.match(r'^[a-zA-Z\s]+$', title):
            raise forms.ValidationError("Title should only contain letters and spaces.")
        return title

    def clean_message(self):
        message = self.cleaned_data.get('message')
        if not message:
            raise forms.ValidationError("Message is required.")
        if len(message) < 5:
            raise forms.ValidationError("Message must be at least 5 characters long.")
        return message

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        message = cleaned_data.get('message')

        if message and not re.match(r'^[a-zA-Z0-9\s.,!?]+$', message):
            raise forms.ValidationError({
                'message': "Message should only contain letters, numbers, spaces, and basic punctuation (.,!?)."
            })

        if title and message:
            if title == message:
                raise forms.ValidationError("Title and message cannot be identical.")

        return cleaned_data
    




class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'category']

class QueryForm(forms.ModelForm):
    class Meta:
        model = Query
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter query title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Describe your query'}),
        }


from django import forms
from .models import AdminResponse

class AdminResponseForm(forms.ModelForm):
    class Meta:
        model = AdminResponse
        fields = ['response_text']  # ✅ Use the correct field name
        widgets = {
            'response_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter your response...'}),
        }

