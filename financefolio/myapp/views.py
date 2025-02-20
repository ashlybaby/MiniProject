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
from django.shortcuts import render, redirect, get_object_or_404
from .models import Query
from django.contrib.auth.decorators import user_passes_test


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
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt  # Consider removing this in production
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.utils.dateparse import parse_date
from .forms import BudgetForm, ExpenseForm
from django.contrib import messages
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.dateparse import parse_date
from decimal import Decimal
from .forms import BudgetForm, ExpenseForm
from .models import Budget, Expense, Goal
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

@login_required
@csrf_exempt  # Use with caution; consider using CSRF tokens for production
def budget_view(request):
    expense_form = ExpenseForm()  # Instantiate the ExpenseForm here

    if request.method == 'POST':
        budget_form = BudgetForm(request.POST)
        actual_income = request.POST.get('actual-income')
        summary = None  # Initialize summary to avoid UnboundLocalError

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
            remove_expenses = request.POST.getlist('remove-expense')  # Get list of expenses to remove

            # Clear existing expenses if editing an existing budget
            if not created:
                budget.expenses.all().delete()

            # Remove specified expenses
            for remove_id in remove_expenses:
                try:
                    expense_to_remove = Expense.objects.get(id=remove_id, budget=budget)
                    category = expense_to_remove.category
                    expense_value = expense_to_remove.actual_expense

                    # Update the related goal
                    goals = Goal.objects.filter(user=request.user, category=category)
                    for goal in goals:
                        goal.current_amount -= expense_value
                        if goal.current_amount < goal.target_amount:
                            goal.status = 'ongoing'  # Update status if needed
                        goal.save()

                    expense_to_remove.delete()  # Delete the expense
                except Expense.DoesNotExist:
                    continue  # Ignore if the expense does not exist

            # Add new expenses
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

                # Validation to ensure the expense date is within the budget month and is not in the future
                if category and actual_expenses[i] and expense_date:
                    if not (expense_date.year == selected_month.year and expense_date.month == selected_month.month):
                        budget_form.add_error('month', "Expense date must be within the selected budget month.")
                        break  # Exit the loop if validation fails

                    # Check if the expense date is in the future
                    from datetime import date as date_today
                    if expense_date > date_today.today():
                        budget_form.add_error('month', "Expense date cannot be in the future.")
                        break  # Exit the loop if validation fails

                    # Create the expense
                    Expense.objects.create(
                        budget=budget,
                        category=category,
                        actual_expense=expense_value,
                        date=expense_date  # Set the date field
                    )

                    # Update the Goal current_amount based on the new expense
                    goals = Goal.objects.filter(user=request.user, category=category)
                    for goal in goals:
                        goal.current_amount += expense_value
                        if goal.current_amount >= goal.target_amount:
                            goal.status = 'completed'
                        goal.save()

            # Calculate summary details only if there are no validation errors
            if not budget_form.errors:
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

            # Render with form errors if there were validation issues
            if budget_form.errors:
                return render(request, 'budget.html', {
                    'form': budget_form,
                    'expense_form': expense_form,  # Pass expense form
                    'errors': budget_form.errors
                })

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



 
from django.shortcuts import render
from .forms import GoalForm
@login_required
def goal_view(request):
    form = GoalForm()  # Create an instance of the form
    return render(request, 'goal_tracking.html', {'form': form})  # Pass the form to the template


from .models import Budget, Expense
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import GoalForm
from .models import Budget

from django.contrib import messages  # Import messages

@login_required  # Ensure that the user is logged in
def add_goal(request):
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user  # Attach the goal to the current logged-in user

            # Select the most recent budget for the current user
            budget = Budget.objects.filter(user=request.user).order_by('-created_at').first()

            if not budget:
                messages.error(request, 'No budget found.')  # Use messages to display error
                return render(request, 'goal_tracking.html', {'form': form})

            # Associate the goal with the most recent budget
            goal.budget = budget
            goal.save()  # Save the goal in the database

            messages.success(request, 'Goal saved successfully!')  # Success message
            return redirect('user_dashboard')  # Redirect to dashboard
        else:
            print("Form is not valid:", form.errors)  # Debug invalid form
    else:
        form = GoalForm()

    return render(request, 'goal_tracking.html', {'form': form})

# views.py

from .models import Expense, Budget
from django.db.models import Sum
from .models import Budget, Expense
from django.http import JsonResponse
from django.utils import timezone



def get_current_amount(request):
    if request.method == "GET":
        category = request.GET.get('category')
        user = request.user

        # Ensure category is provided
        if not category:
            return JsonResponse({'error': 'Category is required'}, status=400)

        # Get the current month and year
        now = timezone.now()
        current_month = now.month
        current_year = now.year

        # Get user's budgets
        user_budgets = Budget.objects.filter(user=user)

        # Check if user has budgets
        if not user_budgets.exists():
            return JsonResponse({'error': 'No budgets found for user'}, status=404)

        # Calculate total expenses for the selected category in the current month
        total_spent_current_month = Expense.objects.filter(
            budget__in=user_budgets,
            category=category,
            date__year=current_year,
            date__month=current_month
        ).aggregate(Sum('actual_expense'))['actual_expense__sum'] or 0

        # Calculate total expenses for the selected category for the entire period
        total_spent_entire = Expense.objects.filter(
            budget__in=user_budgets,
            category=category
        ).aggregate(Sum('actual_expense'))['actual_expense__sum'] or 0

        # Return the result as JSON
        return JsonResponse({
            'current_amount': total_spent_current_month,
            'total_expense': total_spent_entire,
            'message': "Click here to see total expenses for this category"
        })



# View for editing an existing goal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Goal  # Ensure your Goal model is imported
from .forms import GoalForm  # Ensure your GoalForm is imported

# View for editing an existing goal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .forms import GoalForm
from .models import Goal
@login_required
def edit_goal(request):
    if request.method == 'POST':
        goal_id = request.POST.get('id')
        print("Received goal ID:", goal_id)  # Debugging: Check received goal ID
        goal = get_object_or_404(Goal, id=goal_id, user=request.user)
        
        form = GoalForm(request.POST, instance=goal)
        print("Form data:", request.POST)
        print("Goal object before update:", goal)

        if form.is_valid():
            form.save()
            messages.success(request, 'Goal updated successfully!')
            return redirect('user_dashboard')
        else:
            print("Form errors:", form.errors)  # Print errors if the form is invalid

    else:  # If the request method is GET, we load the form with the goal data.
        goal_id = request.GET.get('id')
        goal = get_object_or_404(Goal, id=goal_id, user=request.user)
        form = GoalForm(instance=goal)

    return render(request, 'edit_goal.html', {'form': form})





from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Goal  # Make sure to import your Goal model



def delete_goal(request, goal_id):  # Accepts 'goal_id'
    if request.method == 'POST':
        goal = get_object_or_404(Goal, id=goal_id, user=request.user)  # Uses goal_id
        goal.delete()
        messages.success(request, 'Goal deleted successfully!')
        return redirect('user_dashboard')

    return redirect('user_dashboard')  # Handle other request methods


# views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Goal
from django.db.models import Sum
from .models import Goal, Expense  # Make sure to import Expense model
from django.utils import timezone
from django.shortcuts import render
from .models import Expense, Goal

@login_required
def goal_progress(request):
    # Get the current date to filter expenses by the current month and year
    current_date = timezone.now()
    current_month = current_date.month
    current_year = current_date.year
    
    # Fetch the user's goals
    goals = Goal.objects.filter(user=request.user)
    progress_data = []

    for goal in goals:
        # Calculate total spent for the goal's category in the current month
        total_spent = Expense.objects.filter(
            budget__user=request.user,
            category=goal.category,
            date__year=current_year,  # Filter by the current year
            date__month=current_month  # Filter by the current month
        ).aggregate(Sum('actual_expense'))['actual_expense__sum'] or 0
        
        # Update the current_amount with the total spent for the current month
        goal.current_amount = total_spent

        # Calculate progress percentage
        if goal.target_amount > 0:
            progress_percentage = (goal.current_amount / goal.target_amount) * 100
        else:
            progress_percentage = 0

        # Determine the status of the goal
        if goal.current_amount >= goal.target_amount:
            goal_status = 'failed'  # Goal has been achieved
        elif current_date.date() > goal.deadline:
            goal_status = 'completed'  # Goal has not been achieved, and the deadline passed
        else:
            goal_status = 'ongoing'  # Goal is ongoing

        # Append goal data to progress_data
        progress_data.append({
            'goal': goal,
            'progress': progress_percentage,
            'status': goal_status  # Updated status to reflect ongoing, completed, or failed
        })

    context = {
        'progress_data': progress_data
    }

    return render(request, 'goal_progress.html', context)


from django.shortcuts import render
from django.http import JsonResponse
from .models import Budget, Expense
from django.db.models import Sum

def history_views(request):
    # Get the current user’s budgets
    budgets = Budget.objects.filter(user=request.user)
    history_data = []

    for budget in budgets:
        # Filter expenses for each budget and order by date
        expenses = Expense.objects.filter(budget=budget).order_by('date')

        # Calculate total actual expenses for this budget
        total_actual_expenses = sum(exp.actual_expense for exp in expenses)

        history_data.append({
            'month': budget.month.strftime('%B %Y'),  # Assuming month is a DateField
            'planned_income': budget.planned_income,
            'actual_income': budget.actual_income,
            'expenses': total_actual_expenses,  # Updated to show total actual expenses
            'balance': budget.remaining_balance_actual(),  # Calculate balance
            'expense_dates': [exp.date.strftime('%Y-%m-%d') for exp in expenses],  # Add expense dates
            'expense_amounts': [exp.actual_expense for exp in expenses],  # Add expense amounts per date
        })

    # Prepare data for the chart
    labels = [data['month'] for data in history_data]
    planned_income_data = [data['planned_income'] for data in history_data]
    actual_income_data = [data['actual_income'] for data in history_data]
    expenses_data = [data['expenses'] for data in history_data]

    return render(request, 'history.html', {
        'history_data': history_data,
        'labels': labels,
        'planned_income_data': planned_income_data,
        'actual_income_data': actual_income_data,
        'expenses_data': expenses_data,
    })


#admin#

# views.py
# views.py

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from .models import Goal  # Ensure you import the Goal model correctly
from django.utils import timezone
from django.db.models import Sum
from .models import Goal, Expense


@user_passes_test(lambda u: u.is_superuser)
def goals_overview(request):
    # Get the current date and time
    current_date = timezone.now()
    current_month_start = current_date.replace(day=1)  # Get the start of the current month

    # Fetch all goals
    goals = Goal.objects.all()
    goal_summary = []

    for goal in goals:
        # Calculate total spent for the goal's category in the current month
        total_spent_in_current_month = Expense.objects.filter(
            budget__user=goal.user,  # Filter by the user who owns the goal
            category=goal.category,  # Filter by the goal's category
            date__gte=current_month_start  # Only include expenses from the current month onwards
        ).aggregate(Sum('actual_expense'))['actual_expense__sum'] or 0  # Set to 0 if no expenses found

        # Update the current amount for the goal
        goal.current_amount = total_spent_in_current_month

        # Calculate the progress percentage
        progress_percentage = 0
        if goal.target_amount > 0:  # Prevent division by zero
            progress_percentage = (goal.current_amount / goal.target_amount) * 100

        # Determine the goal status
        if goal.target_amount >= goal.current_amount:
            goal_status = 'completed'  # Goal has been completed
            progress_percentage = 100
            progress_color='#4CAF50'
        elif current_date.date() > goal.deadline:
            goal_status = 'failed'
            progress_percentage = 100  # Goal deadline has passed without achieving the target
            progress_color = '#f44336'
        else:
            goal_status = 'ongoing' # Goal is still in progress
            progress_color = '#ff9800' # Determine the progress bar color based on goal completion
            progress_percentage = (goal.current_amount / goal.target_amount) * 100 

        # Build the summary data for each goal
        summary = {
            'user_email': goal.user.email,
            'goal_name': goal.name,
            'target_amount': float(goal.target_amount),  # Convert to float for JSON serialization
            'current_amount': float(goal.current_amount),  # Convert to float for JSON serialization
            'status': goal_status,  # Updated status (ongoing, completed, or failed)
            'deadline': goal.deadline,
            'progress_percentage': round(progress_percentage, 1),  # Round to 1 decimal place
            'progress_color': progress_color,  # Added color for progress bar
        }
        goal_summary.append(summary)

    # Render the goals overview page with the updated data
    return render(request, 'goals_overview.html', {
        'goal_summary': goal_summary,
    })



from django.shortcuts import render, get_object_or_404
from .models import Budget, Expense, Goal
from django.db.models import Sum
from django.contrib.auth import get_user_model
User = get_user_model()  # Get the custom user model
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import user_passes_test
from .models import User, Budget, Expense, Goal  # Ensure you have the correct imports
from django.core import serializers
from django.shortcuts import render
from .models import User, Budget, Expense, Goal  # Adjust import to match your models
from decimal import Decimal
import json
from django.core.serializers.json import DjangoJSONEncoder

from decimal import Decimal
import json
from django.shortcuts import render
from django.db.models import Sum
from django.core.serializers.json import DjangoJSONEncoder
from .models import User, Budget, Expense, Goal

def financial_report_all_users(request):
    if request.user.is_authenticated:
        # Get all users in the system excluding the superuser
        users = User.objects.exclude(is_superuser=True)

        # Prepare the report data for each user
        user_reports = []
        for user in users:
            # Get all budgets for the user
            budgets = Budget.objects.filter(user=user)

            if budgets.exists():
                # Assume you're interested in the most recent budget's month/year
                recent_budget = budgets.order_by('-month').first()  # Get the most recent budget
                month_year = recent_budget.month.strftime('%B %Y')  # Format as "Month Year"

                # Aggregate actual income for the user's budgets (no planned income)
                total_actual_income = budgets.aggregate(Sum('actual_income'))['actual_income__sum'] or Decimal('0')

                # Aggregate total expenses for the user's budgets
                total_expenses = Expense.objects.filter(budget__in=budgets).aggregate(Sum('actual_expense'))['actual_expense__sum'] or Decimal('0')

                # Get goals for the user
                goals = Goal.objects.filter(user=user)

                # Prepare goal data
                goal_data = []
                for goal in goals:
                    # Determine the goal status
                    status = 'Success' if float(goal.current_amount) >= float(goal.target_amount) else 'Success'

                    goal_data.append({
                        'name': goal.name,
                        'target_amount': float(goal.target_amount),
                        'current_amount': float(goal.current_amount),
                        'status': status,
                        'deadline': goal.deadline.strftime('%Y-%m-%d'),
                    })

                # Add this user's report data to the list
                user_reports.append({
                    'user_name': user.first_name or user.email,
                    'month_year': month_year,
                    'total_actual_income': float(total_actual_income),
                    'total_expenses': float(total_expenses),
                    'goals': goal_data,
                })
            else:
                # No data tracked for this user
                user_reports.append({
                    'user_name': user.first_name or user.email,
                    'month_year': 'N/A',  # No budgets
                    'total_actual_income': 0.0,
                    'total_expenses': 0.0,
                    'goals': [],
                    'message': 'User has not tracked anything yet',  # Custom message
                })

        # Convert report data to JSON (if needed for JavaScript use)
        user_reports_json = json.dumps(user_reports, cls=DjangoJSONEncoder)

        # Prepare the context data for the template
        context = {
            'user_reports': user_reports,
            'user_reports_json': user_reports_json,
        }

        return render(request, 'reports.html', context)
    else:
        return render(request, 'error.html', {'message': 'You need to log in to view the financial reports.'})


from django.shortcuts import render
from .models import Expense, Goal
from django.db.models import Sum
from .models import Expense, Budget, Goal
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Expense, Goal, Budget
from django.db.models import Sum

@login_required
def recommendations_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user_budgets = Budget.objects.filter(user=request.user)
    category_expenses = Expense.objects.filter(budget__in=user_budgets).values('category').annotate(total_spent=Sum('actual_expense'))
    user_goals = Goal.objects.filter(user=request.user, status='active')

    recommendations = []
    for goal in user_goals:
        total_spent_in_category = next((expense['total_spent'] for expense in category_expenses if expense['category'] == goal.category), 0)

        if total_spent_in_category >= goal.target_amount:
            recommendation = {
                'title': f"Limit Spending in {goal.category}",
                'description': f"Consider limiting spending in {goal.category} to meet your goal for {goal.name}.",
                'category': goal.category
            }
        else:
            remaining = goal.target_amount - total_spent_in_category
            recommendation = {
                'title': f"On Track for {goal.name}",
                'description': f"You're on track to meet your goal for {goal.name}. You can spend up to ${remaining:.2f} more in {goal.category}.",
                'category': goal.category
            }
        recommendations.append(recommendation)

    context = {
        'category_expenses': category_expenses,
        'goals': user_goals,
        'recommendations': recommendations,
    }

    return render(request, 'recommendations.html', context)


#announcement#
from django.shortcuts import render
from django.http import JsonResponse
from .models import Announcement

def announcement_list(request):
    announcements = Announcement.objects.all().order_by('-created_at')
    context = {
        'announcements': announcements,
    }
    return render(request, 'create_announcement.html', context)



from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from .forms import AnnouncementForm

# Check if user is admin
def is_admin(user):
    return user.is_admin

from django.shortcuts import redirect, render
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from .models import Announcement
from django.contrib import messages
from .forms import AnnouncementForm

def is_admin(user):
    return user.is_superuser  # Update this to match your admin check logic

def is_admin(user):
    return user.is_staff or user.is_superuser

@user_passes_test(is_admin)
def create_announcement(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()
            messages.success(request, 'Announcement created successfully!')
            return redirect('create_announcement')  # Stay on the same page to show the success message
        else:
            print(form.errors)  # Output validation errors to console
    else:
        form = AnnouncementForm()

    # Fetch all announcements to display when the view is loaded
    announcements = Announcement.objects.all().order_by('-created_at')

    return render(request, 'create_announcement.html', {'form': form, 'announcements': announcements})


@user_passes_test(is_admin)
def edit_announcement(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Announcement updated successfully!')
            return redirect('create_announcement')
    else:
        form = AnnouncementForm(instance=announcement)

    announcements = Announcement.objects.all().order_by('-created_at')
    return render(request, 'create_announcement.html', {
        'form': form,
        'announcements': announcements,
        'edit_mode': True,
        'announcement_to_edit': announcement_id
  
  })
from django.views.decorators.http import require_POST

@require_POST
@user_passes_test(is_admin)
def delete_announcement(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    announcement.delete()
    messages.success(request, 'Announcement deleted successfully!')
    return redirect('create_announcement')


from django.shortcuts import render
from django.db.models import Sum
from .models import Expense
from django.db.models.functions import TruncMonth
from .models import Expense, Budget, Goal
from django.contrib.auth.decorators import login_required
from django.utils import timezone

@login_required
def category_detail(request, category):
    # Get all budgets for the user
    user_budgets = Budget.objects.filter(user=request.user)
    
    # Get all expenses for the user in the specified category
    expenses = Expense.objects.filter(budget__in=user_budgets, category=category).order_by('-date')
    
    # Calculate total for the year
    current_year = timezone.now().year
    yearly_total = expenses.filter(date__year=current_year).aggregate(total=Sum('actual_expense'))['total'] or 0

    # Calculate monthly totals for the current year
    monthly_totals = expenses.filter(date__year=current_year)\
        .annotate(month=TruncMonth('date'))\
        .values('month')\
        .annotate(total=Sum('actual_expense'))\
        .order_by('-month')

    # Get related goals
    related_goals = Goal.objects.filter(user=request.user, category=category)

    # Get category display name
    category_display = dict(Expense.CATEGORIES).get(category, category)

    context = {
        'category': category,
        'category_display': category_display,
        'expenses': expenses,
        'yearly_total': yearly_total,
        'monthly_totals': monthly_totals,
        'related_goals': related_goals,
    }
    return render(request, 'category_detail.html', context)

from django.http import JsonResponse
from .models import Announcement

def get_announcements(request):
    announcements = Announcement.objects.all().order_by('-created_at')
    data = [
        {
            'title': ann.title,
            'content': ann.message,
            'date_created': ann.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        for ann in announcements
    ]
    return JsonResponse({'announcements': data})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Article
from .forms import ArticleForm  # Create an ArticleForm in your forms.py

def is_admin(user):
    return user.is_staff or user.is_superuser# Adjust this based on your custom admin role check

@login_required
@user_passes_test(is_admin)
def add_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            return redirect('admin_articles_list')
    else:
        form = ArticleForm()
    return render(request, 'admin_add_article.html', {'form': form})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Article
from .forms import ArticleForm

@login_required
@user_passes_test(is_admin)
def admin_articles_list(request):
    articles = Article.objects.order_by('-date_posted')
    article_forms = [ArticleForm(instance=article) for article in articles]
    return render(request, 'admin_articles_list.html', {'article_forms': article_forms})

from django.shortcuts import render, get_object_or_404, redirect
from .models import Article
from .forms import ArticleForm

@login_required
@user_passes_test(is_admin)
def edit_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, f'Article "{article.title}" has been updated successfully.')
            return redirect('admin_articles_list')
    else:
        form = ArticleForm(instance=article)
    return render(request, 'edit_article.html', {'form': form, 'article': article})


from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages


@login_required
@user_passes_test(is_admin)
def delete_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.method == 'POST':
        title = article.title  # Store title before deletion
        article.delete()
        messages.success(request, f'Article "{title}" has been deleted successfully.')
        return redirect('admin_articles_list')
    return render(request, 'admin_confirm_delete_article.html', {'article': article})


from .models import Query
from .forms import QueryForm

@login_required
def submit_query(request):
    if request.method == 'POST':
        form = QueryForm(request.POST)
        if form.is_valid():
            query = form.save(commit=False)
            query.user = request.user
            query.save()
            return redirect('query_list')
    else:
        form = QueryForm()
    return render(request, 'submit_query.html', {'form': form})

@login_required
def query_list(request):
    queries = Query.objects.filter(user=request.user)
    return render(request, 'query_list.html', {'queries': queries})

def admin_required(user):
    return user.is_authenticated and user.is_admin

@user_passes_test(admin_required)
def admin_query_list(request):
    queries = Query.objects.all().order_by('-created_at')
    return render(request, 'admin/query_list.html', {'queries': queries})

@user_passes_test(admin_required)
def admin_update_query_status(request, query_id):
    query = get_object_or_404(Query, id=query_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Query.STATUS_CHOICES):  # Check if the status is valid
            query.status = status
            query.save()
            return redirect('admin_query_list')

    return render(request, 'admin/update_query_status.html', {'query': query, 'status_choices': Query.STATUS_CHOICES})


from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def add_goal(request):
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user  # Attach the goal to the current logged-in user

            # Select the most recent budget for the current user
            budget = Budget.objects.filter(user=request.user).order_by('-created_at').first()

            if not budget:
                messages.error(request, 'No budget found.')  # Use messages to display error
                return render(request, 'goal_tracking.html', {'form': form})

            # Associate the goal with the most recent budget
            goal.budget = budget
            goal.save()  # Save the goal in the database

            messages.success(request, 'Goal saved successfully!')  # Success message
            return redirect('add_goal')  # Redirect to the same page to show success message
        else:
            print("Form is not valid:", form.errors)  # Debug invalid form
    else:
        form = GoalForm()

    return render(request, 'goal_tracking.html', {'form': form})



from django.shortcuts import render
from .models import Article

def articles_page(request):
    articles = Article.objects.all()  # Fetch all articles from the database
    return render(request, 'articles_page.html', {'articles': articles})  # Pass articles to the template

    #--------------------------------------------------------------------------------------------------------------------------
    #ML implementation

    # views.py
import csv
import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse
from sklearn.linear_model import LinearRegression
from .models import Expense
from datetime import date, timedelta

def export_to_csv(request):
    """Export the latest database data to a CSV file and serve it to the user."""
    file_path = 'expenses.csv'
    expenses = Expense.objects.all()

    # Write data to the CSV file dynamically
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Month', 'category', 'Planned Income', 'Actual Income', 'Expenses', 'Balance'])
        for expense in expenses:
            writer.writerow([
                expense.month,
                expense.category,
                expense.planned_income,
                expense.actual_income,
                expense.expenses,
                expense.balance,
            ])

    # Serve the CSV file to the user
    with open(file_path, 'r', encoding='utf-8') as file:
        response = HttpResponse(file, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="expenses.csv"'
        return response
#.......................................................................................#
#undoed latest future expense#
# def predict_future_expense(request):
#     """Predict future expenses for 2025 using historical data with seasonality and category trends."""
#     import pandas as pd
#     from django.shortcuts import render
#     from statsmodels.tsa.seasonal import seasonal_decompose
#     from statsmodels.tsa.holtwinters import ExponentialSmoothing
#     import numpy as np

#     # Path to your CSV file
#     file_path = 'expenses.csv'

#     # Load the data
#     try:
#         df = pd.read_csv(file_path)
#     except FileNotFoundError:
#         return render(request, 'predict_expense.html', {
#             'error': 'The CSV file does not exist. Please upload the correct file.'
#         })

#     # Ensure the necessary columns are present
#     if not {'category', 'amount', 'date'}.issubset(df.columns):
#         return render(request, 'predict_expense.html', {
#             'error': 'The CSV file must contain "category", "amount", and "date" columns.'
#         })

#     # Convert the date column to datetime format
#     df['date'] = pd.to_datetime(df['date'])

#     # Aggregate monthly expenses by category
#     df['month'] = df['date'].dt.to_period('M')
#     monthly_expenses_by_category = df.groupby(['month', 'category'])['amount'].sum().reset_index()
#     monthly_expenses_by_category['month'] = monthly_expenses_by_category['month'].dt.to_timestamp()

#     # Ensure sufficient data for seasonal decomposition
#     if len(monthly_expenses_by_category['month'].unique()) < 24:  # Minimum 2 years of data
#         return render(request, 'predict_expense.html', {
#             'error': 'Insufficient data for accurate prediction. At least 2 years of data are required.'
#         })

#     # Perform forecasting for each category
#     predictions_by_category = []
#     for category, group in monthly_expenses_by_category.groupby('category'):
#         try:
#             # Perform seasonal decomposition
#             decomposition = seasonal_decompose(group['amount'], model='additive', period=12)
#             trend = decomposition.trend
#             seasonal = decomposition.seasonal
#             residual = decomposition.resid

#             # Use Holt-Winters Exponential Smoothing for forecasting
#             model = ExponentialSmoothing(
#                 group['amount'],
#                 seasonal='add',
#                 seasonal_periods=12,
#                 trend='add'
#             )
#             model_fit = model.fit()

#             # Predict expenses for 2025
#             future_dates = pd.date_range(start=group['month'].iloc[-1] + pd.offsets.MonthEnd(1), periods=12, freq='M')
#             predicted_expenses = model_fit.forecast(steps=12)
#             predictions = pd.DataFrame({
#                 'month': future_dates,
#                 'category': category,
#                 'predicted_expense': predicted_expenses
#             })
#             predictions_by_category.append(predictions)
#         except Exception as e:
#             print(f"Error processing category {category}: {e}")
#             continue

#     predictions_by_category = pd.concat(predictions_by_category, ignore_index=True)

#     # Prepare context for the template
#     context = {
#         'historical_data': monthly_expenses_by_category.to_html(index=False, classes='table table-bordered'),
#         'predictions': predictions_by_category.to_html(index=False, classes='table table-bordered')
#     }

#     return render(request, 'predict_expense.html', context)




import pandas as pd
import joblib
from django.shortcuts import render
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# File paths
models_file_path = 'expense_prediction_models.pkl'
csv_file_path = 'expenses.csv'

def predict_future_expense(request):
    try:
        # Load trained models
        models = joblib.load(models_file_path)
    except FileNotFoundError:
        return render(request, 'predict_expense.html', {
            'error': 'Prediction models not found. Please train the models first.'
        })

    try:
        # Load historical expense data
        df = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        return render(request, 'predict_expense.html', {
            'error': 'The CSV file does not exist. Please upload the correct file.'
        })

    # Ensure required columns exist
    required_columns = {'category', 'amount', 'date'}
    if not required_columns.issubset(df.columns):
        return render(request, 'predict_expense.html', {
            'error': 'CSV file must contain "category", "amount", and "date" columns.'
        })

    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])  # Drop rows with invalid dates

    # Aggregate expenses per month and category
    df['month'] = df['date'].dt.to_period('M')
    monthly_data = df.groupby(['month', 'category'])['amount'].sum().reset_index()
    monthly_data['month'] = monthly_data['month'].dt.to_timestamp()

    predictions_list = []

    # Get last recorded month for forecasting start
    if not monthly_data.empty:
        last_month = monthly_data['month'].max()
        future_dates = pd.date_range(start=last_month + pd.offsets.MonthEnd(1), periods=12, freq='M')

        # Predict expenses for each category
        for category, group in monthly_data.groupby('category'):
            try:
                model = models.get(category)
                if model:
                    predicted_expenses = model.forecast(steps=12)
                    category_predictions = pd.DataFrame({
                        'month': future_dates,
                        'category': category,
                        'predicted_expense': predicted_expenses.round(2)
                    })
                    predictions_list.append(category_predictions)
                else:
                    print(f"No model found for category: {category}")
            except Exception as e:
                print(f"Error predicting for category {category}: {e}")

    # Combine predictions
    if predictions_list:
        predictions_df = pd.concat(predictions_list, ignore_index=True)
    else:
        predictions_df = pd.DataFrame(columns=['month', 'category', 'predicted_expense'])

    # Convert DataFrame to HTML tables for rendering
    context = {
        'historical_data': monthly_data.to_html(index=False, classes='table table-bordered'),
        'predictions': predictions_df.to_html(index=False, classes='table table-bordered')
    }

    return render(request, 'predict_expense.html', context)


from sklearn.linear_model import LinearRegression
from datetime import date, timedelta
from django.http import HttpResponse 
from django.shortcuts import render
import pandas as pd
from .models import Expense

def read_csv(request):
    """Read the expenses from the database and save to CSV dynamically."""
    expenses = Expense.objects.all()

    # Prepare the data for CSV and machine learning
    data = []
    for expense in expenses:
        data.append([expense.date, expense.category, float(expense.actual_expense)])

    # Create a DataFrame and save to CSV
    df = pd.DataFrame(data, columns=['date', 'category', 'actual_expense'])
    csv_file_path = 'expenses.csv'
    df.to_csv(csv_file_path, index=False)

    # Prepare data for machine learning
    df['date_numeric'] = pd.to_datetime(df['date']).map(lambda x: x.toordinal())  # Convert dates to numeric
    df['category_num'] = pd.factorize(df['category'])[0]  # Encode categories as numeric

    X = df[['date_numeric', 'category_num']]
    y = df['actual_expense']

    # Train a machine learning model
    model = LinearRegression()
    model.fit(X, y)

    # Predict future expenses for the next 30 days
    today = date.today()
    future_dates = [today + timedelta(days=i) for i in range(1, 31)]
    future_data = pd.DataFrame({
        'date_numeric': [d.toordinal() for d in future_dates],
        'category_num': [0] * len(future_dates)  # Assuming a default category
    })
    

    future_data['predicted_expense'] = model.predict(future_data[['date_numeric', 'category_num']])

# Convert negative values to positive
    future_data['predicted_expense'] = future_data['predicted_expense'].abs()

# Combine predictions with dates
    future_data['date'] = future_dates
    print(future_data['date'])
    

    future_predictions = future_data[['date', 'predicted_expense']]

    
    print(future_predictions)

    # Render the predictions and the current expense data
    return render(request, 'display_expenses.html', {
        'data': df.to_html(classes='table table-bordered'),
        'predictions': future_predictions.to_html(classes='table table-bordered')
    })

def add_expense(request):
    """Add an expense to the database and update the CSV file."""
    if request.method == 'POST':
        # Extract form data
        budget_id = request.POST['budget_id']
        category = request.POST['category']
        actual_expense = request.POST['actual_expense']
        expense_date = request.POST['date']

        # Save to the database
        Expense.objects.create(
            budget_id=budget_id,
            category=category,
            actual_expense=actual_expense,
            date=expense_date
        )

        # Update the CSV file
        read_csv(request)

        return HttpResponse("Expense added successfully!")

def download_csv(request):
    """Serve the dynamically updated CSV file."""
    file_path = 'expenses.csv'
    with open(file_path, 'r', encoding='utf-8') as file:
        response = HttpResponse(file, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="expenses.csv"'
        return response
    

#chatbot#
# __________________________________________________________________________________#
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def chatbot(request):
    if request.method == "POST":
        try:
            # Parse the incoming data as JSON
            body = json.loads(request.body)
            user_message = body.get("message", "").lower()  # Safely retrieve the message

            # Logic for handling finance-related questions
            if "spend" in user_message:
                reply = "Please check your available balance and spend expense based on that."
            
            elif "save" in user_message:
                reply = "Try saving at least 20% of your income for future goals."
            elif "hi" in user_message:
                reply = "Hi .How can I assist you today"
            elif"How are you" in user_message:
                reply = "Fine.Hope you are also fine.How can you assiist you today"
            elif "goal" in user_message:
                reply = "Check goal progress section for knowing about your goal.You can set new goals using set goal feature"
            elif "emergency fund" in user_message:
                 reply = "An emergency fund should cover 3 to 6 months of your living expenses. Start small and gradually build it up."
            elif "investment" in user_message:
                 reply = "Consider diversifying your investments into stocks, bonds, mutual funds, or real estate. Always research or consult a financial advisor."
            elif "retirement" in user_message:
                  reply = "Start saving for retirement early. Contributing to a retirement fund like a 401(k) or IRA is a great way to prepare for the future."
            elif "save" in user_message:
                  reply = "Try saving at least 20% of your income for future goals. You can allocate it to an emergency fund, investments, or retirement savings."
            elif "feedback" in user_message:
                  reply = "Please check feedback from dashboard.You can find feedback from other users"
            elif "expense" in user_message:
                  reply = "Please check the dashboard and use expense tracker to store your day today expenses"
            elif "hello" in user_message:
                  reply = "Hello,How can I assist you today"
            elif "how are you" in user_message:
                  reply = "Fine.How can I assist you today"
            elif "who are you" in user_message:
                  reply = "I am a software program on internet"
            elif "income" in user_message:

                  reply = "Please check expense  tracker or history to know about your income"
            elif "recommandation" in user_message:
                  reply = "please check recommendation button avilable in dashboard to see personalized recommendation for you based on your goal progress"
            else:
                reply = "I am not sure how to help with that. Would you please ask about finance management-related questions?"

            # Return a successful JSON response
            return JsonResponse({"reply": reply}, status=200)

        except json.JSONDecodeError:
            # Handle invalid JSON error
            return JsonResponse({"error": "Invalid JSON data received."}, status=400)

    # If not POST, return an error message
    return JsonResponse({"error": "Invalid request method."}, status=405)

#feedback#


from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Feedback

def feedback_list1(request):
    # Handle search functionality
    query = request.GET.get('q', '')  # Get search query from URL parameters
    feedbacks = Feedback.objects.filter(feedback_text__icontains=query).order_by('-created_at')

    # Pagination
    paginator = Paginator(feedbacks, 10)  # Show 10 feedbacks per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Render feedback list with pagination and search query
    return render(request, 'feedback_list.html', {
        'feedbacks': page_obj,
        'query': query
    })
def feedback_list11(request):
    # Handle search functionality
    query = request.GET.get('q', '')  # Get search query from URL parameters
    feedbacks = Feedback.objects.filter(feedback_text__icontains=query).order_by('-created_at')

    # Pagination
    paginator = Paginator(feedbacks, 10)  # Show 10 feedbacks per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Render feedback list with pagination and search query
    return render(request, '404.html', {
        'feedbacks': page_obj,
        'query': query
    })

#articles#
from .models import Article  # Import your Article model

def articles_list(request):
    articles = Article.objects.order_by('-date_posted')  # Get articles ordered by date
    return render(request, 'articles_list.html', {'articles': articles})


#guidance#
def guidance_view(request):
    """View to display website usage guidance."""
    return render(request, 'guidance.html')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import QueryForm
from .models import Query


from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import QueryForm
@login_required
def submit_query(request):
    if request.method == "POST":
        form = QueryForm(request.POST)
        if form.is_valid():
            query = form.save(commit=False)
            query.user = request.user  # Associate query with logged-in user
            query.save()
            messages.success(request, "Your query has been submitted successfully!")
            return redirect("submit_query")  # Redirect back to the form after submission
    else:
        form = QueryForm()
    
    return render(request, "submit_query.html", {"form": form})


@login_required
def user_query_list(request):
    queries = Query.objects.filter(user=request.user)  # Fetch queries for the logged-in user
    return render(request, 'user_queries.html', {'queries': queries})

from django.shortcuts import get_object_or_404

@login_required
def cancel_query(request, query_id):
    query = get_object_or_404(Query, id=query_id, user=request.user)  # Ensure the query belongs to the user
    query.status = 'C'  # Mark the query as 'Closed'
    query.save()
    messages.success(request, "Your query has been canceled successfully!")
    return redirect('user_query_list')

# from django.contrib.admin.views.decorators import staff_member_required

# @staff_member_required
from django.shortcuts import render
from .models import Query

def admin_query_list(request):
    queries = Query.objects.all()  # Fetch all queries
    return render(request, 'admin_queries.html', {'queries': queries})

@login_required
def resolve_query(request, query_id):
    query = get_object_or_404(Query, id=query_id)
    query.status = 'R'  # Mark as 'Resolved'
    query.save()
    messages.success(request, "Query has been resolved!")
    return redirect('admin_query_list')


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Query

@login_required
def view_queries(request):
    queries = Query.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'submit_query.html', {'queries': queries})



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Query
from .forms import QueryForm

def edit_query(request, query_id):
    query = get_object_or_404(Query, id=query_id)
    if request.method == "POST":
        form = QueryForm(request.POST, instance=query)
        if form.is_valid():
            form.save()
            messages.success(request, "Query updated successfully!")  # Success message
            return redirect('edit_query', query_id=query.id)  # Stay to show message
    else:
        form = QueryForm(instance=query)

    return render(request, 'edit_query.html', {'form': form})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Query

def delete_query(request, query_id):
    query = get_object_or_404(Query, id=query_id, user=request.user)
    
    if request.method == "POST":
        query.delete()
        messages.success(request, "Query deleted successfully.")
        return redirect("submit_query")  # Redirect after deletion

    return render(request, "user_query_list.html")  # Fallback

from django.shortcuts import render, get_object_or_404, redirect
from .models import Query, AdminResponse
from .forms import AdminResponseForm  # Ensure this form is created
from django.contrib.auth.decorators import login_required

@login_required
def admin_response_view(request, query_id):
    query = get_object_or_404(Query, id=query_id)
    responses = AdminResponse.objects.filter(query=query).order_by('-responded_at')

    if request.method == 'POST':
        form = AdminResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.admin = request.user
            response.query = query
            response.save()
            return redirect('admin_response', query_id=query.id)  # Redirect to prevent form resubmission
    else:
        form = AdminResponseForm()

    return render(request, 'admin_response.html', {'query': query, 'responses': responses, 'form': form})



from django.shortcuts import render
from .models import Query, AdminResponse

def user_queries(request):
    queries = Query.objects.filter(user=request.user).prefetch_related('response')
    return render(request, 'user_quries.html', {'queries': queries})

from django.shortcuts import render
from .models import Article

def guest_article_demo(request):
    articles = Article.objects.all().order_by('-date_posted')  # Fetch all articles sorted by date
    return render(request, 'guest_article_demo.html', {'articles': articles})

#new change challenge#

from .models import Challenge, UserChallenge, Reward
from django.contrib.auth.decorators import login_required
from .models import Challenge, UserChallenge

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Challenge, UserChallenge

@login_required
def challenge_list(request):
    # Get unique challenges
    challenges = Challenge.objects.all().distinct()

    # Get only unique active user challenges
    user_challenges = UserChallenge.objects.filter(user=request.user, is_completed=False).distinct()

    # Remove duplicates using a set
    unique_challenges = list(set(challenges))

    return render(request, 'challenge_list.html', {
        'challenges': unique_challenges,
        'user_challenges': user_challenges
    })


@login_required
def accept_challenge(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    
    # Check if the challenge is already accepted by the user
    existing_challenge = UserChallenge.objects.filter(user=request.user, challenge=challenge).exists()
    
    if not existing_challenge:
        UserChallenge.objects.create(user=request.user, challenge=challenge)
    
    return redirect('challenge_list')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserChallenge, Reward

@login_required
def update_progress(request, challenge_id, amount):
    # Get the user's challenge instance
    user_challenge = get_object_or_404(UserChallenge, user=request.user, challenge_id=challenge_id)
    
    # Update the progress of the user challenge
    user_challenge.update_progress(amount)

    # Check if the challenge is completed
    if user_challenge.is_completed:
        # Create or get the reward for the user
        reward, created = Reward.objects.get_or_create(user=request.user)
        reward.add_points(user_challenge.earned_points)

    # Redirect to the challenge list view to display updated challenges
    return redirect('challenge_list')  # Ensure 'challenge_list' is the name of your URL pattern for the challenge list


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ChallengeForm
from .models import Challenge  # ✅ Import the Challenge model for duplicate checking
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ChallengeForm
from .models import Challenge

@login_required
def add_challenge(request):
    if request.method == "POST":
        form = ChallengeForm(request.POST)

        if form.is_valid():
            challenge_name = form.cleaned_data['name']

            # ✅ Check if challenge already exists before saving
            if Challenge.objects.filter(name=challenge_name).exists():
                return JsonResponse({"success": False, "message": "Challenge already exists."}, status=400)

            form.save()
            messages.success(request, "Challenge added successfully!")  # ✅ Store the success message

            # ✅ Return messages in JSON response
            return JsonResponse({
                "success": True, 
                "message": "Challenge added successfully!"
            })
        
        return JsonResponse({"success": False, "errors": form.errors}, status=400)

    else:
        form = ChallengeForm()

    return render(request, 'add_challenge.html', {'form': form})


# from django.http import JsonResponse
# from .forms import ChallengeForm
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from .models import Challenge  # Import your Challenge model

# @login_required
# def add_challenge(request):
#     if request.method == "POST":
#         form = ChallengeForm(request.POST)
#         if form.is_valid():
#             # Check if a challenge with the same name already exists
#             challenge_name = form.cleaned_data['name']  # Assuming 'name' is a field in your ChallengeForm
#             existing_challenge = Challenge.objects.filter(name=challenge_name).first()

#             if existing_challenge:
#                 return JsonResponse({"success": False, "message": "Challenge already exists."}, status=400)

#             # Save the new challenge
#             form.save()
#             messages.success(request, "Challenge added successfully!")
#             return JsonResponse({"success": True, "message": "Challenge added successfully!"})
#         else:
#             # Log the form errors for debugging
#             print("Form errors:", form.errors)  # Print errors to the console
#             return JsonResponse({"success": False, "errors": form.errors}, status=400)

#     else:
#         form = ChallengeForm()

#     return render(request, 'add_challenge.html', {'form': form})




from django.shortcuts import render
from .models import UserChallenge, Expense
from django.utils import timezone

def user_challenge_expenses(request):
    user = request.user
    active_challenges = UserChallenge.objects.filter(user=user)

    # Prepare a dictionary to hold challenge scores
    challenge_scores = {}

    for user_challenge in active_challenges:
        # Get the challenge start and end dates
        start_date = user_challenge.start_date
        end_date = start_date + timezone.timedelta(days=user_challenge.challenge.duration_days)

        # Fetch expenses that fall within the challenge date range
        expenses = Expense.objects.filter(
            budget__user=user,  # Assuming the Budget model has a ForeignKey to User
            date__range=(start_date, end_date)
        )

        # Calculate the total expenses for the challenge
        total_expense = sum(expense.actual_expense for expense in expenses)

        # Store the total expense in the challenge_scores dictionary
        challenge_scores[user_challenge.challenge.id] = {
            'challenge': user_challenge.challenge,
            'total_expense': total_expense,
            'score': 0  # Initialize score
        }

        # Calculate score based on the total expense and challenge target amount
        if total_expense >= user_challenge.challenge.target_amount:
            challenge_scores[user_challenge.challenge.id]['score'] = user_challenge.challenge.points

    return render(request, 'user_challenge_expenses.html', {
        'active_challenges': active_challenges,
        'challenge_scores': challenge_scores
    })
#-----------------------------------------------------------------------------------#


from django.shortcuts import render
from django.contrib import messages
from .forms import QuizQuestionForm

@login_required
def add_quiz_question(request):
    form = QuizQuestionForm()

    if request.method == "POST":
        form = QuizQuestionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Question submitted successfully!")  # Success message
            form = QuizQuestionForm()  # Reset form after success
        else:
            messages.error(request, "There was an error submitting the question. Please check the form.")  # Error message

    return render(request, "admin_add_question.html", {"form": form})


from django.shortcuts import render
from .models import QuizQuestion

@login_required
def take_quiz(request):
    if request.method == "POST":
        user_answers = request.POST
        questions = QuizQuestion.objects.all()
        results = []
        unanswered_questions = []

        for question in questions:
            user_answer = user_answers.get(f'question_{question.id}')
            if not user_answer:  # Check for unanswered questions
                unanswered_questions.append(question)
            else:
                is_correct = user_answer == question.correct_option
                results.append({
                    'question': question.question,
                    'user_answer': user_answer,
                    'correct_answer': question.correct_option,
                    'explanation': question.explanation,
                    'is_correct': is_correct
                })

        if unanswered_questions:
            return render(request, 'quiz.html', {
                'questions': questions,
                'error': "All questions are mandatory. Please answer all questions before submitting."
            })

        return render(request, 'quiz_result.html', {'results': results})

    questions = QuizQuestion.objects.all()
    return render(request, 'quiz.html', {'questions': questions})

def quiz_results(request):
    # Example: Assuming results is a list of dictionaries
    results = [
        {"question": "What is 2 + 2?", "user_answer": "4", "correct_answer": "4", "is_correct": True, "explanation": "Basic math"},
        {"question": "Capital of France?", "user_answer": "London", "correct_answer": "Paris", "is_correct": False, "explanation": "Paris is the capital"},
        # Add more results as needed
    ]

    total_questions = len(results)
    correct_answers = sum(1 for result in results if result["is_correct"])  # Count correct answers

    return render(request, 'quiz_results.html', {
        'results': results,
        'total_questions': total_questions,
        'correct_answers': correct_answers
    })
