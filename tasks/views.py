from django.shortcuts import render
from django.http import HttpResponse
from .models import Event, Participant
from datetime import date

def Home_page(request):
    return render(request, 'Home_page.html')


def Event_details_view(request):
    return render(request, 'Event_details.html')

def Contact_us_view(request):
    return render(request, 'Contact_us.html')

def About_us_view(request):
    return render(request, 'About_us.html')

def Services_view(request):
    return render(request, 'Services.html')

def dashboard(request):
    today = date.today()

    total_events = Event.objects.count()
    upcoming_events = Event.objects.filter(date__gt=today).count()
    past_events = Event.objects.filter(date__lt=today).count()
    total_participants = Participant.objects.count()

    todays_events = Event.objects.filter(date=today)

    context = {
        'total_events': total_events,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'total_participants': total_participants,
        'todays_events': todays_events,
    }

    return render(request, 'dashboard.html', context)