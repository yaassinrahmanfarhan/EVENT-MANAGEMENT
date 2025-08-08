from django.urls import path
from tasks.views import (
    Home_page,
    Event_details_view,
    Contact_us_view,
    About_us_view,
    Services_view
)
from . import views

urlpatterns = [
    # Static Pages
    path('', Home_page, name='home'),  # root URL for home page
    path('home/', Home_page, name='home'),  # optional lowercase URL
    path('event/<int:event_id>/', Event_details_view, name='event_details'),
    path('contact/', Contact_us_view, name='contact_us'),
    path('about/', About_us_view, name='about_us'),
    path('services/', Services_view, name='services'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Event CRUD
    path('events/', views.event_list, name='event_list'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:pk>/update/', views.event_update, name='event_update'),
    path('events/<int:pk>/delete/', views.event_delete, name='event_delete'),

    # RSVP Actions
    path('events/<int:event_id>/rsvp/', views.rsvp_event, name='rsvp_event'),
    path('events/<int:event_id>/cancel-rsvp/', views.cancel_rsvp_event, name='cancel_rsvp_event'),

    # Participant Management
    path('participants/', views.participant_list, name='participant_list'),
    path('participants/create/', views.participant_create, name='participant_create'),
    path('participants/<int:pk>/update/', views.participant_update, name='participant_update'),
    path('participants/<int:pk>/delete/', views.participant_delete, name='participant_delete'),

    # Category CRUD
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
]
