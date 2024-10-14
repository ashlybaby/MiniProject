from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm as BaseUserChangeForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from django.contrib.auth.hashers import make_password
from django import forms
from django.core.exceptions import ValidationError

from .models import User
from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date
from django.contrib.auth.hashers import make_password
from .models import User

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


from django.contrib.auth import authenticate
from django import forms
from .models import User

from django import forms
from django.contrib.auth import authenticate
from .models import User  # Adjust the import based on your User model

class UserLoginForm(forms.Form):
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



from django import forms
from django.contrib.auth import authenticate
from .models import User  # Replace with the path to your custom User model

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

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model

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


from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import ValidationError

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

#class BudgetForm(forms.ModelForm):
    #month = forms.DateField(
        #widget=forms.DateInput(attrs={'type': 'month'}),
        #input_formats=['%Y-%m']  # Accepts YYYY-MM format
    #)
    #class Meta:
        #model = Budget
        #fields = ['month', 'planned_income']

#class ExpenseForm(forms.ModelForm):
    #class Meta:
        ##fields = ['category', 'planned_expense', 'actual_expense']
from django import forms
from .models import Budget, Expense
from django.core.exceptions import ValidationError
import re
from decimal import Decimal

# Custom validation for positive numbers
def validate_positive(value):
    if value < 0:
        raise ValidationError("Value cannot be negative.")

# Custom validation for category field to ensure it's not a number
def validate_category(value):
    if value.isdigit():
        raise ValidationError("Category cannot be a number.")
    # Optionally, check for invalid characters
    if not re.match(r'^[a-zA-Z\s]+$', value):  # Allow letters and spaces only
        raise ValidationError("Category can only contain letters and spaces.")

class BudgetForm(forms.ModelForm):
    month = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'month'}),
        input_formats=['%Y-%m']  # Accepts YYYY-MM format
    )
    planned_income = forms.DecimalField(validators=[validate_positive])

    class Meta:
        model = Budget
        fields = ['month', 'planned_income']

    def clean(self):
        cleaned_data = super().clean()
        planned_income = cleaned_data.get('planned_income')

        if planned_income is not None and planned_income < Decimal('0.00'):
            self.add_error('planned_income', "Planned income cannot be negative.")

        return cleaned_data

class ExpenseForm(forms.ModelForm):
    category = forms.CharField(validators=[validate_category])
    planned_expense = forms.DecimalField(validators=[validate_positive])
    actual_expense = forms.DecimalField(validators=[validate_positive])

    class Meta:
        model = Expense
        fields = ['category', 'planned_expense', 'actual_expense']

    def __init__(self, *args, actual_income=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.actual_income = actual_income

    def clean(self):
        cleaned_data = super().clean()
        planned_expense = cleaned_data.get('planned_expense')
        actual_expense = cleaned_data.get('actual_expense')
        category = cleaned_data.get('category')

        # Validate that actual income is not zero
        if self.actual_income is not None and self.actual_income <= Decimal('0.00'):
            raise ValidationError("You cannot add expenses because your received income is 0.")

        # Validate that planned_expense is positive
        if planned_expense is not None and planned_expense < Decimal('0.00'):
            self.add_error('planned_expense', "Planned expense cannot be negative.")

        # Validate that actual_expense is positive
        if actual_expense is not None and actual_expense < Decimal('0.00'):
            self.add_error('actual_expense', "Actual expense cannot be negative.")

        # Validate category (if needed)
        if category and category.isdigit():
            self.add_error('category', "Category cannot be a number.")

        return cleaned_data

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