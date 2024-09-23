from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm as BaseUserChangeForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from django.contrib.auth.hashers import make_password

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from .models import User
from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from .models import User
from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from .models import User
from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
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
            except User.DoesNotExist:
                # User not registered
                raise forms.ValidationError('You are not registered. Please sign up.')

            # Authenticate the user (checks password)
            user = authenticate(email=email, password=password)
            if user is None:
                raise forms.ValidationError('Invalid email or password')
            if not user.is_active:
                raise forms.ValidationError('Your account is disabled.')

        return cleaned_data


    
from django import forms
from django.contrib.auth import authenticate
from .models import User  # Replace with the path to your custom User model

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


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New password'}),
        strip=False
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'}),
        strip=False
    )


# forms.py

#from django import forms
#from django.contrib.auth.forms import UserChangeForm
#from .models import User

#class CustomUserChangeForm(UserChangeForm):
    #class Meta:
        #model = User
        #fields = ['first_name', 'last_name', 'email', 'gender', 'age', 'address', 'city', 'state']
from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import User

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'gender', 'age', 'address', 'city', 'state']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove password fields
        self.fields.pop('password')
        self.fields.pop('password2', None)  # In case there's a second password field

#........................................................................................................#
from django import forms
from .models import Budget, Expense

class BudgetForm(forms.ModelForm):
    month = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'month'}),
        input_formats=['%Y-%m']  # Accepts YYYY-MM format
    )

    class Meta:
        model = Budget
        fields = ['month', 'planned_income']

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'planned_expense', 'actual_expense']
