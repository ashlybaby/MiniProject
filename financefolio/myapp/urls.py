from django.contrib import admin
from django.urls import path
from myapp import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from .views import user_dashboard
from .views import CustomPasswordResetView, CustomPasswordResetConfirmView, CustomPasswordResetCompleteView

urlpatterns = [
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='custom_password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('', views.index, name="index"),
    path('about/', views.about, name='about'),
    path('home/', views.home, name='index'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register, name='register'),
    path('guest_view/', views.guest_view, name='guest_view'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('admin_dashboard',views.admin_dashboard,name='admin_dashboard'),
    path('login/',views.user_login,name='user_login'),
    path('customadmin/', views.admin_login, name='admin_login'),
    path('user_dashboard/',login_required(user_dashboard), name='user_dashboard'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='custom_password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='custom_password_reset_complete.html'), name='password_reset_complete'),
    path('accounts/login/', views.user_login, name='user_login'),
    path('logout/', views.custom_logout, name='logout'),
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/',views.profile_edit, name='profile_edit'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('budget/', views.budget_view, name='budget_view'),
    path('api/history/', views.history_view, name='history_view'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('api/users/', views.UserListView.as_view(), name='user_list'),
    path('financial-videos/', views.financial_management_videos, name='financial_videos'),
    path('feedback/', views.submit_feedback, name='submit_feedback'),
    path('feedback/list', views.feedback_list, name='feedback-list'),
    path('toggle_user_activation/<int:user_id>/', views.toggle_user_activation, name='toggle_user_activation'),
    path('goal_view/',views.goal_view,name='goal_view'),
    path('add-goal/', views.add_goal, name='add_goal'),
    path('get-current-amount/', views.get_current_amount, name='get_current_amount'),
    path('edit_goal/', views.edit_goal, name='edit_goal'),
    path('delete_goal/<int:goal_id>/', views.delete_goal, name='delete_goal'),
    path('goal-progress/', views.goal_progress, name='goal_progress'),
    path('history/', views.history_views, name='history_views'),
    path('goals_overview/', views.goals_overview, name='goals_overview'),
    path('reports/all/', views.financial_report_all_users, name='financial_report_all_users'),
    path('recommendations_view/', views.recommendations_view, name='recommendations_view'),
]
    


    



  

    
    
          




