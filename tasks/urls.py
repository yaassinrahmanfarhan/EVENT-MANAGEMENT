from django.urls import path
from tasks.views import Home_page, Event_details_view
urlpatterns = [
    path('Home/', Home_page, name='Home'),
    path('Event-details-view/', Event_details_view, name='Event-details'),
]