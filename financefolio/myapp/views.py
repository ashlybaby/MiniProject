from django.shortcuts import render,redirect
from django.contrib import messages
from .models import User
from .forms import RegistrationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from .forms import UserLoginForm, AdminLoginForm
from django.urls import reverse
from django.contrib.auth import authenticate
from django.contrib.auth.views import PasswordResetDoneView
from django.shortcuts import render, redirect
from .forms import CustomUserChangeForm
from datetime import date
from .forms import RegistrationForm
from decimal import Decimal



def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')

def home(request):
    return render(request, 'index.html')

def guest_view(request):
    return render(request, 'guestlogin.html')

def forgot_password(request):
    return render(request, 'custom_password_reset_form.html')

def recover(request):
    return render(request, 'custom_password_reset_form.html')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Calculate age from birth_date
            birth_date = form.cleaned_data.get('birth_date')
            if birth_date:
                today = date.today()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            else:
                age = None  # Or handle as appropriate if birth_date is not provided

            # Create and save the user with all relevant fields
            user = User.objects.create_user(
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                password=form.cleaned_data['password'],
                gender=form.cleaned_data['gender'],
                age=age,  # Use the dynamically calculated age
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state']
            )
            user.save()

            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('user_login')  # Redirect to the login page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    return redirect(reverse('user_dashboard'))  # Redirect to home or another appropriate page
                else:
                    messages.error(request, 'Your account is disabled.')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = UserLoginForm()

    return render(request, 'user_login.html', {'form': form})

#@login_required
#def user_dashboard(request):
    return render(request, 'userdashboard.html')


from django.shortcuts import render, redirect
from django.urls import reverse
@login_required
def user_dashboard(request):
    if request.user.is_superuser:
        return redirect(reverse('admin_dashboard'))  # Replace with the URL you want to redirect to
    return render(request, 'userdashboard.html')



def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(email=email, password=password)
            if user is not None and user.is_superuser:
                auth_login(request, user)
                return redirect(reverse('admin_dashboard'))  # Redirect to the admin dashboard
        else:
            messages.error(request, 'Invalid credentials or permissions.')
    else:
        form = AdminLoginForm()

    return render(request, 'admin_login.html', {'form': form})


@login_required
def admin_dashboard(request):
    return render(request, 'customadmindashboard.html')


# views.py


from django.shortcuts import redirect
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse

def custom_logout(request):
    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect(reverse('index'))  # Redirect to the home page or login page
    else:
        return redirect('index')  # Redirect to the user dashboard if not a POST request


from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .forms import CustomPasswordResetForm, CustomSetPasswordForm

class CustomPasswordResetView(auth_views.PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'custom_password_reset_form.html'
    success_url = reverse_lazy('password_reset_done')


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'custom_password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


from django.contrib.auth.views import PasswordResetCompleteView

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        # Redirect to the custom login page
        return redirect('user_login')



@login_required
def profile_view(request):
    # Get the currently authenticated user
    user = request.user
    
    # Pass the user object to the template
    context = {
        'user': user,
    }
    return render(request, 'profile.html', context)

#def profile_edit(request):
    return redirect('profile.html')



@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile_edit')  # Redirect to the same page to show the message
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    return render(request, 'profile_edit.html', {'form': form})

#...................................................................................................................#
from django.shortcuts import render
from django.http import JsonResponse
from .models import Budget, Expense
from .forms import BudgetForm, ExpenseForm
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect

from django.shortcuts import render
from django.http import JsonResponse
from .models import Budget, Expense
from .forms import BudgetForm

from django.shortcuts import render
from .models import Budget, Expense
from .forms import BudgetForm
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Use with caution; consider using CSRF tokens for production
def budget_view(request):
    if request.method == 'POST':
        budget_form = BudgetForm(request.POST)
        actual_income = request.POST.get('actual-income')

        if budget_form.is_valid():
            # Create budget instance but don't save yet
            budget = budget_form.save(commit=False)
            budget.user = request.user  # Assign the logged-in user

            # Validate and convert actual_income to Decimal if necessary
            if actual_income:
                try:
                    budget.actual_income = Decimal(actual_income)
                except ValueError:
                    budget.actual_income = None  # Handle invalid input

            # Save the budget
            budget.save()

            # Handle expense entries
            expense_categories = request.POST.getlist('expense-category')
            planned_expenses = request.POST.getlist('planned-expense')
            actual_expenses = request.POST.getlist('actual-expense')

            for i in range(len(expense_categories)):
                Expense.objects.create(
                    budget=budget,
                    category=expense_categories[i],
                    planned_expense=planned_expenses[i],
                    actual_expense=actual_expenses[i]
                )

            # Prepare the summary
            summary = {
                'planned_income': budget.planned_income,
                'actual_income': budget.actual_income,
                'total_planned_expenses': budget.total_planned_expenses(),
                'total_actual_expenses': budget.total_actual_expenses(),
                'remaining_balance_planned': budget.remaining_balance_planned(),
                'remaining_balance_actual': budget.remaining_balance_actual()
            }

            return render(request, 'budget.html', {
                'form': BudgetForm(), 
                'summary': summary, 
                'success_message': 'Budget added successfully!'
            })

        # If the form is not valid, re-render with errors
        return render(request, 'budget.html', {
            'form': budget_form, 
            'errors': budget_form.errors
        })

    # For GET requests, render the empty form
    return render(request, 'budget.html', {'form': BudgetForm()})

# views.py

from django.http import JsonResponse
from django.db.models import Sum, F
from .models import Budget  # Make sure to import your actual model

from django.shortcuts import render
from .models import Budget, Expense

from django.http import JsonResponse

def history_view(request):
    budgets = Budget.objects.all()
    history_data = []

    for budget in budgets:
        expenses = Expense.objects.filter(budget=budget)
        total_planned_expenses = sum(exp.planned_expense for exp in expenses)
        total_actual_expenses = sum(exp.actual_expense for exp in expenses)

        history_data.append({
            'month': budget.month,  # Assuming you have a month field in Budget
            'planned_income': budget.planned_income,
            'actual_income': budget.actual_income,
            'expenses': total_actual_expenses,  # Updated to show total actual expenses
            'balance': budget.remaining_balance_actual(),  # Adjust this if needed
        })

    return JsonResponse(history_data, safe=False)  # Return data as JSON

from django.http import JsonResponse
from django.shortcuts import render
from .models import User  # Adjust import based on your user model

def manage_users(request):
    if request.method == 'POST':
        users = list(User.objects.values('id', 'first_name', 'last_name', 'email'))  # Adjust fields as needed
        return JsonResponse(users, safe=False)

    return render(request, 'admin_dashboard.html')  # Replace with your actual template name



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, 'User deleted successfully.')
    return redirect('manage_users')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import User  # Adjust the import based on your User model's location

@csrf_exempt
def delete_user(request, user_id):
    if request.method == 'DELETE':
        user = get_object_or_404(User, id=user_id)  # Fetch the user by ID
        user.delete()  # Delete the user
        return JsonResponse({'message': 'User deleted successfully.'}, status=200)
    
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

from django.http import JsonResponse
from django.views import View
from .models import User  # Adjust based on your user model

class UserListView(View):
    def get(self, request):
        users = User.objects.all().values('id', 'first_name', 'last_name', 'email', 'is_staff')
        return JsonResponse(list(users), safe=False)
    
    