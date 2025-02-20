from django.contrib import admin
from django.urls import path
from myapp import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from .views import user_dashboard
from .views import CustomPasswordResetView, CustomPasswordResetConfirmView, CustomPasswordResetCompleteView
from django.conf.urls import include

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
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('create-announcement/', views.create_announcement, name='create_announcement'),
    path('edit_announcement/<int:announcement_id>/', views.edit_announcement, name='edit_announcement'),
    path('delete_announcement/<int:announcement_id>/',views.delete_announcement, name='delete_announcement'),
    path('category/<str:category>/', views.category_detail, name='category_detail'),
    path('api/announcements/', views.get_announcements, name='get_announcements'),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('articles/', views.admin_articles_list, name='admin_articles_list'),
    path('articles/add/', views.add_article, name='add_article'),
    path('articles/<int:article_id>/edit/', views.edit_article, name='edit_article'),
    path('articles/<int:article_id>/delete/', views.delete_article, name='delete_article'),
    path('submit-query/', views.submit_query, name='submit_query'),
    path('queries/', views.query_list, name='query_list'),
    path('admin/queries/', views.admin_query_list, name='admin_query_list'),
    path('admin/queries/<int:query_id>/update/', views.admin_update_query_status, name='admin_update_query_status'),

    path('articles_page/', views.articles_page, name='articles_page'),  # Ensure this line is present

     path('edit_goal/<int:goal_id>/', views.edit_goal, name='edit_goal'),  # Ensure this line is present
    #----------------------------------------------------------------------------------------
    #ml implementation
    path('predict-expense/', views.predict_future_expense, name='predict_expense'),  # Predict future expense
    path('display-expenses/', views.read_csv, name='display_expenses'),  # Display expense data
    path('read_csv/', views.read_csv, name='read_csv'),
    path('add_expense/', views.add_expense, name='add_expense'),
    path('download_csv/', views.download_csv, name='download_csv'),
    path('feedback_list1/', views.feedback_list1,name='feedback_list1'),
    path('feedbacklist11/',views.feedback_list11,name='feedback_list11'),
    path('articles_list/' ,views.articles_list,name='articles_list'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('guidance_view/',views.guidance_view,name='guidance_view'),
    path('user_query_list/',views.user_query_list, name='user_query_list'),
    path('query/cancel/<int:query_id>/', views.cancel_query, name='cancel_query'),
    path('admin_query_list/', views.admin_query_list, name='admin_query_list'),
    path('admin/query/resolve/<int:query_id>/', views.resolve_query, name='resolve_query'),
    path('view-queries/', views.view_queries, name='view_queries'),
    path('query/edit/<int:query_id>/', views.edit_query, name='edit_query'),
    path('query/delete/<int:query_id>/', views.delete_query, name='delete_query'),
    path('response/<int:query_id>/', views.admin_response_view, name='admin_response'),
    path('guest/articles/', views.guest_article_demo, name='guest_article_demo'),
    path('challenges/', views.challenge_list, name='challenge_list'),
    path('challenges/accept/<int:challenge_id>/', views.accept_challenge, name='accept_challenge'),
    path('challenges/update/<int:challenge_id>/<int:amount>/', views.update_progress, name='update_progress'),
    path('add-challenge/', views.add_challenge, name='add_challenge'),
    path('user-challenge-expenses/', views.user_challenge_expenses, name='user_challenge_expenses'),
    path('add-question/', views.add_quiz_question, name='add_quiz_question'),
    path('quiz/', views.take_quiz, name='take_quiz'),
]




    




    

    
 # URL path to view the CSV data
    # This URL will trigger the 'read_csv' view





    


    



  

    
    
          




