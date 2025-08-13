from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView, PasswordChangeView, PasswordChangeDoneView

urlpatterns = [
    path('', views.Home_page, name='home'),
    path('home/', views.Home_page, name='home'),

    # Authentication
    path('signup/', views.signup_view, name='signup'),
    path('activate/<int:user_id>/<token>/', views.activate_account, name='activate_account'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.LogoutGetView.as_view(), name='logout'),

    # Dashboards by role
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/organizer/', views.organizer_dashboard, name='organizer_dashboard'),
    path('dashboard/participant/', views.participant_dashboard, name='participant_dashboard'),

    # Public pages
    path('contact/', views.Contact_us_view.as_view(), name='contact_us'),
    path('about/', views.About_us_view.as_view(), name='about_us'),
    path('services/', views.Services_view.as_view(), name='services'),

    # Event details and list
    path('events/', views.event_list.as_view(), name='event_list'),
    path('events/<int:event_id>/', views.Event_details_view, name='event_details'),

    # Event CRUD (Organizer & Admin)
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:pk>/update/', views.event_update, name='event_update'),
    path('events/<int:pk>/delete/', views.event_delete, name='event_delete'),

    # RSVP (Participant only)
    path('events/<int:event_id>/rsvp/', views.rsvp_event, name='join_event'),
    path('events/<int:event_id>/cancel-rsvp/', views.cancel_rsvp_event, name='cancel_event'),

    # Category CRUD (Organizer & Admin)
    path('categories/', views.category_list.as_view(), name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # Participant management (Admin only)
    path('participants/', views.participant_list.as_view(), name='participant_list'),
    path('participants/create/', views.participant_create, name='participant_create'),
    path('participants/<int:pk>/update/', views.participant_update, name='participant_update'),
    path('participants/<int:pk>/delete/', views.participant_delete, name='participant_delete'),
    
    path('groups/', views.group_list.as_view(), name='group_list'),
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/<int:pk>/update/', views.group_update, name='group_update'),
    path('groups/<int:pk>/delete/', views.group_delete, name='group_delete'),
     path("manage-roles/", views.manage_roles, name="manage_roles"),

    path('profile/', views.ProfileView.as_view(template_name='accounts/profile.html'), name='profile'),
    path('password-change/', views.ChangePassword.as_view(), name='password_change'),
    # path('password-change/', PasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'), name='password_change_done'),
]
