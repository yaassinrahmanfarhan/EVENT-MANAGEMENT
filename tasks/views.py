from django.shortcuts import render
from django.http import HttpResponse


def Home_page(request):
    return render(request, 'Home_page.html')


def Event_details_view(request):
    return render(request, 'Event_details.html')

def Contact_us_view(request):
    return render(request, 'Contact_us.html')