from django.urls import path
from tasks.views import (Home_page, Event_details_view, Contact_us_view,
    About_us_view, Services_view)
from . import views

urlpatterns = [
    path('Home/', Home_page, name='Home'),
    path('Event-details-view/<int:event_id>/', Event_details_view, name='Event-details'),
    path('Contact-us/', Contact_us_view, name='Contact-us'),
    path('About-us/', About_us_view, name='About-us'),
    path('Services/', Services_view, name='Services'),
    path('dashboard/', views.dashboard, name='dashboard'),

#Event CRUD
    path('events/', views.event_list, name='event_list'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/update/<int:pk>/', views.event_update, name='event_update'),
    path('events/delete/<int:pk>/', views.event_delete, name='event_delete'),



#User/Participant Management
    path('participants/', views.participant_list, name='participant_list'),
    path('participants/create/', views.participant_create, name='participant_create'),
    path('participants/update/<int:pk>/', views.participant_update, name='participant_update'),
    path('participants/delete/<int:pk>/', views.participant_delete, name='participant_delete'),

#Category CRUD
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/update/<int:pk>/', views.category_update, name='category_update'),
    path('categories/delete/<int:pk>/', views.category_delete, name='category_delete'),
]