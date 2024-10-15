from django.shortcuts import render,redirect
from django.contrib import messages
from .models import User
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from .forms import UserLoginForm, AdminLoginForm
from django.urls import reverse
from django.contrib.auth import authenticate
from django.contrib.auth.views import PasswordResetDoneView
from .forms import CustomUserChangeForm
from datetime import date
from .forms import RegistrationForm
from decimal import Decimal
from django.views.decorators.cache import never_cache


@never_cache
def index(request):
    if request.user.is_authenticated and request.user.is_active:
        return redirect(reverse('user_dashboard'))  # Redirect authenticated user to the dashboard
    return render(request, 'index.html')  

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')

@never_cache
def home(request):
    if request.user.is_authenticated and request.user.is_active:
        # Optionally, you can ensure the user is logged in (though they should already be)
        # auth_login(request, request.user)  # Not necessary if the user is already authenticated
        return redirect(reverse('user_dashboard'))
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

# def user_login(request):
#     if request.method == 'POST':
#         form = UserLoginForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data.get('email')
#             password = form.cleaned_data.get('password')
#             user = authenticate(email=email, password=password)
#             if user is not None:
#                 if user.is_active:
#                     auth_login(request, user)
#                     return redirect(reverse('user_dashboard'))  # Redirect to home or another appropriate page
#                 else:
#                     messages.error(request, 'Your account is disabled.')
#             else:
#                 messages.error(request, 'Invalid email or password.')
#     else:
#         form = UserLoginForm()

#     return render(request, 'user_login.html', {'form': form})
from django.views.decorators.cache import never_cache
#new change user login#
@never_cache
def user_login(request):
    if request.user.is_authenticated:
        return redirect(reverse('user_dashboard'))
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    return redirect(reverse('user_dashboard'))  # Redirect to dashboard or appropriate page
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

@never_cache
@login_required
def admin_dashboard(request):
    if request.user.is_superuser:
        return render(request, 'customadmindashboard.html')  # Render admin dashboard for superusers
    else:
        messages.error(request, "You do not have the required permissions to access this page.")
        return redirect(reverse('user_dashboard'))  

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



@never_cache
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
    #return redirect('profile.html')


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from .forms import CustomUserChangeForm

@never_cache
@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        
        if form.is_valid():
            form.save()
            success_message = 'Profile updated successfully.'
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': success_message
                })
            else:
                messages.success(request, success_message)
                return redirect('userdashboard')  # Redirect to dashboard after non-AJAX update
        else:
            error_message = 'Please correct the errors below.'
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': error_message,
                    'errors': form.errors
                })
            else:
                messages.error(request, error_message)
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    return render(request, 'userdashboard.html', {'form': form})


#...................................................................................................................#

from .forms import BudgetForm, ExpenseForm
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Budget, Expense
from .forms import BudgetForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required


# @login_required
# @csrf_exempt  # Use with caution; consider using CSRF tokens for production
# def budget_view(request):
#     if request.method == 'POST':
#         budget_form = BudgetForm(request.POST)
#         actual_income = request.POST.get('actual-income')

#         if budget_form.is_valid():
#             # Create budget instance but don't save yet
#             budget = budget_form.save(commit=False)
#             budget.user = request.user  # Assign the logged-in user

#             # Validate and convert actual_income to Decimal if necessary
#             if actual_income:
#                 try:
#                     budget.actual_income = Decimal(actual_income)
#                 except ValueError:
#                     budget.actual_income = None  # Handle invalid input

#             # Save the budget
#             budget.save()

#             # Handle expense entries
#             expense_categories = request.POST.getlist('expense-category')
#             planned_expenses = request.POST.getlist('planned-expense')
#             actual_expenses = request.POST.getlist('actual-expense')

#             for i in range(len(expense_categories)):
#                 Expense.objects.create(
#                     budget=budget,
#                     category=expense_categories[i],
#                     planned_expense=planned_expenses[i],
#                     actual_expense=actual_expenses[i]
#                 )

#             # Prepare the summary
#             summary = {
#                 'planned_income': budget.planned_income,
#                 'actual_income': budget.actual_income,
#                 'total_planned_expenses': budget.total_planned_expenses(),
#                 'total_actual_expenses': budget.total_actual_expenses(),
#                 'remaining_balance_planned': budget.remaining_balance_planned(),
#                 'remaining_balance_actual': budget.remaining_balance_actual()
#             }

#             return render(request, 'budget.html', {
#                 'form': BudgetForm(), 
#                 'summary': summary, 
#                 'success_message': 'Budget added successfully!'
#             })

#         # If the form is not valid, re-render with errors
#         return render(request, 'budget.html', {
#             'form': budget_form, 
#             'errors': budget_form.errors
#         })

#     # For GET requests, render the empty form
#     return render(request, 'budget.html', {'form': BudgetForm()})

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt  # Consider removing this in production
from django.shortcuts import render, redirect
from decimal import Decimal
from .forms import BudgetForm
from .models import Budget, Expense

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from decimal import Decimal
from .forms import BudgetForm
from .models import Budget, Expense

from django.shortcuts import render, get_object_or_404
from .models import Budget, Expense
from .forms import BudgetForm, ExpenseForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from django.utils.dateparse import parse_date

from django.shortcuts import render, get_object_or_404
from .models import Budget, Expense
from .forms import BudgetForm, ExpenseForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from django.utils.dateparse import parse_date
from django.utils import timezone

from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from .forms import BudgetForm, ExpenseForm
from .models import Budget, Expense

@login_required
@csrf_exempt  # Use with caution; consider using CSRF tokens for production
def budget_view(request):
    expense_form = ExpenseForm()  # Instantiate the ExpenseForm here

    if request.method == 'POST':
        budget_form = BudgetForm(request.POST)
        actual_income = request.POST.get('actual-income')

        if budget_form.is_valid():
            # Extract the selected month from the form
            selected_month = budget_form.cleaned_data['month']

            # Check if a budget for this month already exists
            budget, created = Budget.objects.get_or_create(
                user=request.user,
                month=selected_month,
                defaults={'planned_income': budget_form.cleaned_data['planned_income']}
            )

            if not created:
                # If the budget already exists, update the planned_income if needed
                budget.planned_income = budget_form.cleaned_data['planned_income']
                budget.save()

                # Optionally, update actual_income if provided
                if actual_income:
                    budget.actual_income = Decimal(actual_income)
                    budget.save()
            else:
                # If a new budget was created, set the actual_income if provided
                if actual_income:
                    budget.actual_income = Decimal(actual_income)
                    budget.save()

            # Handle expense entries
            expense_categories = request.POST.getlist('expense-category')
            actual_expenses = request.POST.getlist('actual-expense')
            custom_categories = request.POST.getlist('custom-category')
            expense_dates = request.POST.getlist('expense-date')  # New: Get list of dates

            # Clear existing expenses if editing an existing budget
            if not created:
                budget.expenses.all().delete()

            for i in range(len(expense_categories)):
                category = expense_categories[i]
                expense_value = Decimal(actual_expenses[i]) if actual_expenses[i] else 0
                expense_date_str = expense_dates[i] if i < len(expense_dates) else None

                # Parse the date string into a date object
                if expense_date_str:
                    expense_date = parse_date(expense_date_str)
                else:
                    expense_date = None

                if category == 'custom' and custom_categories[i]:
                    category = custom_categories[i]

                if category and actual_expenses[i] and expense_date:
                    Expense.objects.create(
                        budget=budget,
                        category=category,
                        actual_expense=expense_value,
                        date=expense_date  # Set the date field
                    )

            # Calculate summary details
            planned_income = budget.planned_income
            actual_income_decimal = Decimal(actual_income) if actual_income else 0
            total_actual_expenses = budget.total_actual_expenses()
            remaining_balance = actual_income_decimal - total_actual_expenses

            summary = {
                'planned_income': planned_income,
                'actual_income': actual_income_decimal,
                'total_actual_expenses': total_actual_expenses,
                'remaining_balance': remaining_balance
            }

            return render(request, 'budget.html', {
                'form': BudgetForm(initial={'month': selected_month, 'planned_income': planned_income}),
                'expense_form': expense_form,  # Pass expense form
                'summary': summary,
                'success_message': 'Budget added/updated successfully!'
            })

        # If the budget form is not valid, render the page with errors
        return render(request, 'budget.html', {
            'form': budget_form,
            'expense_form': expense_form,  # Pass expense form even when budget form fails
            'errors': budget_form.errors
        })

    elif request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Handle AJAX request to fetch existing budget data
        month = request.GET.get('month')
        if month:
            try:
                # Parse the month from 'YYYY-MM' format
                selected_month = parse_date(f"{month}-01")
                if not selected_month:
                    raise ValueError

                budget = Budget.objects.get(user=request.user, month=selected_month)
                expenses = Expense.objects.filter(budget=budget)

                expenses_data = []
                for expense in expenses:
                    expenses_data.append({
                        'category': expense.category,
                        'actual_expense': float(expense.actual_expense),
                        'date': expense.date.strftime('%Y-%m-%d') if expense.date else ''
                    })
               
                summary = {
                    'planned_income': float(budget.planned_income),
                    'actual_income': float(budget.actual_income) if budget.actual_income else 0,
                    'total_actual_expenses': float(budget.total_actual_expenses()),
                    'remaining_balance': float(budget.remaining_balance_actual()) if budget.remaining_balance_actual() is not None else 0
                }

                data = {
                    'summary': summary,
                    'expenses': expenses_data
                }

                return JsonResponse(data, safe=False)
            except (Budget.DoesNotExist, ValueError):
                return JsonResponse({'error': 'No budget found for the selected month.'}, status=404)

    # Handle standard GET request
    return render(request, 'budget.html', {
        'form': BudgetForm(),
        'expense_form': expense_form  # Pass expense form on GET request
    })



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
        users = list(User.objects.values('id', 'first_name', 'last_name', 'email', 'is_active'))  # Include is_active if needed
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
        users = User.objects.all().values('id', 'first_name', 'last_name', 'email', 'is_staff', 'is_active')
        return JsonResponse(list(users), safe=False)

# views.py
from django.shortcuts import render

def financial_management_videos(request):
    return render(request, 'financial_management_videos.html')  # Adjust the template name as needed

#feedback
from django.shortcuts import render, redirect
from .forms import FeedbackForm
from django.contrib import messages

from django.http import JsonResponse
from django.contrib import messages

def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            if request.user.is_authenticated:
                feedback.user = request.user  # Associate feedback with logged-in user
            feedback.save()
            return JsonResponse({'success': True, 'message': 'Thank you for your feedback!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)



# views.py
import json  # Import the json module
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from .models import User  # Import your User model

from django.core.mail import send_mail
import json
from .models import User  # Adjust based on your user model

@require_http_methods(["PATCH"])  # Ensure only PATCH requests are allowed
def toggle_user_activation(request, user_id):
    user = get_object_or_404(User, id=user_id)  # Fetch the user object

    # Parse the request body to get the activation state
    try:
        data = json.loads(request.body)  # Load JSON data from the request body
        is_active = data.get('is_active')  # Get the activation state

        if is_active is not None:  # Ensure is_active is provided
            # Check if the account is being deactivated
            if user.is_active and not is_active:
                # Send an email notification to the user
                send_mail(
                    subject='Account Deactivated - FinanceFolio',
                    message=(
                        'Dear {},\n\nYour account has been deactivated due to suspicious activities.\n'
                        'If you believe this is a mistake, please contact us at financefolio2024@gmail.com.\n\n'
                        'Best regards,\nFinanceFolio Support Team'
                    ).format(user.first_name),
                    from_email='financefolio2024@gmail.com',
                    recipient_list=[user.email],
                    fail_silently=False,
                )

            user.is_active = is_active  # Set the user's activation status
            user.save()  # Save the updated user object

            return JsonResponse({'status': 'success', 'is_active': user.is_active})
        else:
            return JsonResponse({'status': 'error', 'message': 'is_active not provided'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)




# from django.shortcuts import redirect, get_object_or_404
# from django.http import HttpResponseRedirect
# from .models import CustomUser

# def toggle_active_status(request, user_id):
#     user = get_object_or_404(CustomUser, id=user_id)
    
#     if request.method == 'POST':
#         status = request.POST.get('status')
#         current_table = request.POST.get('current_table')  # Get the current table (users or service providers)
        
#         if status == 'deactivate':
#             user.is_active = False
#         elif status == 'activate':
#             user.is_active = True
#         user.save()

#         # Redirect back to the same page with the correct table
#         if current_table == 'users':
#             return HttpResponseRedirect('/admin_dashboard?show=users')
#         elif current_table == 'service_providers':
#             return HttpResponseRedirect('/admin_dashboard? show=service_providers')
    
#     return redirect('view_users')  # Fallback if something goes wrong


# views.py
# from django.http import JsonResponse, HttpResponse
# from django.views.decorators.csrf import csrf_exempt
# from .models import Feedback  # Assuming you have a Feedback model
# from django.contrib.auth.models import User

# def feedback_list(request):
#     if request.method == 'GET':
#         feedbacks = Feedback.objects.select_related('user').all()
#         feedback_data = [
#             {
#                 'id': fb.id,
#                 'user': {
#                     'first_name': fb.user.first_name,
#                     'last_name': fb.user.last_name,
#                 },
#                 'feedback_text': fb.feedback_text,
#             }
#             for fb in feedbacks
#         ]
#         return JsonResponse(feedback_data, safe=False)

# @csrf_exempt
# def delete_feedback(request, feedback_id):
#     if request.method == 'DELETE':
#         try:
#             feedback = Feedback.objects.get(id=feedback_id)
#             feedback.delete()
#             return HttpResponse(status=204)
#         except Feedback.DoesNotExist:
#             return JsonResponse({'error': 'Feedback not found'}, status=404)
#     return JsonResponse({'error': 'Invalid request method'}, status=400)



 # views.py

# views.py
from django.http import JsonResponse
from .models import Feedback

def feedback_list(request):
    feedbacks = Feedback.objects.select_related('user').all()
    feedback_data = []

    for feedback in feedbacks:
        feedback_data.append({
            'username': feedback.user.email if feedback.user else "Guest User",
            'feedback_text': feedback.feedback_text,
            'rating': feedback.rating,
        })

    # Debugging output
    print("Feedback Data:", feedback_data)  # Log the data being returned

    return JsonResponse(feedback_data, safe=False)
