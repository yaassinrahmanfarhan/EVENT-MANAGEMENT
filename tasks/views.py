from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import login
from datetime import date
from .models import Event, Category
from .forms import EventForm, UserRegisterForm, CategoryForm


# ---------------------------
# Home Page
# ---------------------------
def Home_page(request):
    query = request.GET.get('q')
    events = Event.objects.prefetch_related('participant')

    if query:
        events = events.filter(name__icontains=query)

    return render(request, 'Home_page.html', {'events': events, 'query': query})


# ---------------------------
# Event Detail
# ---------------------------
def Event_details_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'Event_details.html', {'event': event})


# ---------------------------
# Static Pages
# ---------------------------
def Contact_us_view(request):
    return render(request, 'Contact_us.html')

def About_us_view(request):
    return render(request, 'About_us.html')

def Services_view(request):
    return render(request, 'Services.html')


# ---------------------------
# Event CRUD
# ---------------------------
def event_list(request):
    events = Event.objects.select_related('category').prefetch_related('participant')

    # Optional Filters
    category_id = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    search = request.GET.get('search')

    if category_id:
        events = events.filter(category_id=category_id)

    if start_date and end_date:
        events = events.filter(date__range=[start_date, end_date])

    if search:
        events = events.filter(Q(name__icontains=search) | Q(location__icontains=search))

    return render(request, 'events/event_list.html', {
        'events': events,
        'categories': Category.objects.all()
    })


def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form})


def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_list')
    else:
        form = EventForm(instance=event)
    return render(request, 'events/event_form.html', {'form': form})


def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        return redirect('event_list')
    return render(request, 'events/event_confirm_delete.html', {'event': event})


# ---------------------------
# RSVP (Join/Leave Event)
# ---------------------------
def rsvp_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.user.is_authenticated:
        event.participant.add(request.user)
    return redirect('event_list')

def cancel_rsvp_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.user.is_authenticated:
        event.participant.remove(request.user)
    return redirect('event_list')


# ---------------------------
# User/Participant Views
# ---------------------------
def participant_list(request):
    participants = User.objects.prefetch_related('rsvp_events')
    return render(request, 'participants/participant_list.html', {'participants': participants})


def participant_create(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Optional: log in immediately after registration
            return redirect('participant_list')
    else:
        form = UserRegisterForm()
    return render(request, 'participants/participant_form.html', {'form': form})


def participant_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('participant_list')
    else:
        form = UserRegisterForm(instance=user)
    return render(request, 'participants/participant_form.html', {'form': form})


def participant_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        return redirect('participant_list')
    return render(request, 'participants/participant_confirm_delete.html', {'participant': user})


# ---------------------------
# Category CRUD
# ---------------------------
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'categories/category_list.html', {'categories': categories})


def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'categories/category_form.html', {'form': form})


def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'categories/category_form.html', {'form': form})


def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'categories/category_confirm_delete.html', {'category': category})


# ---------------------------
# Dashboard / Stats
# ---------------------------
def dashboard(request):
    today = timezone.now().date()
    filter_type = request.GET.get('filter', 'today')

    total_events = Event.objects.count()
    upcoming_events = Event.objects.filter(date__gt=today).count()
    past_events = Event.objects.filter(date__lt=today).count()
    total_participants = User.objects.filter(rsvp_events__isnull=False).distinct().count()
    # Filtering logic for event list
    if filter_type == 'upcoming':
        filtered_events = Event.objects.filter(date__gt=today).order_by('date')
    elif filter_type == 'past':
        filtered_events = Event.objects.filter(date__lt=today).order_by('-date')
    elif filter_type == 'all':
        filtered_events = Event.objects.all().order_by('date')
    elif filter_type == 'participants':
        filtered_events = []  # Could list users who RSVP’d most events
    else:  # default to today's events
        filtered_events = Event.objects.filter(date=today).order_by('time')

    return render(request, 'dashboard.html', {
        'total_events': total_events,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'total_participants': total_participants,
        'filtered_events': filtered_events,
        'filter': filter_type
    })




# from django.shortcuts import render, get_object_or_404, redirect
# from django.db.models import Q,Count
# from django.utils import timezone
# from django.http import HttpResponse
# from .models import Event, Category
# from datetime import date
# from .forms import EventForm, ParticipantForm, CategoryForm
# from django.contrib.auth.models import User

# def Home_page(request):
#     query = request.GET.get('q')
#     events = Event.objects.prefetch_related('User')

#     if query:
#         events = events.filter(name__icontains=query)

#     return render(request, 'Home_page.html', {'events': events, 'query': query})



# def Event_details_view(request, event_id):
#     event = Event.objects.get(id=event_id)
#     return render(request, 'Event_details.html', {'event': event})


# def Contact_us_view(request):
#     return render(request, 'Contact_us.html')

# def About_us_view(request):
#     return render(request, 'About_us.html')

# def Services_view(request):
#     return render(request, 'Services.html')

# def event_list(request):
#     events = Event.objects.select_related('category').prefetch_related('User')

#     # Optional Filters
#     category_id = request.GET.get('category')
#     start_date = request.GET.get('start_date')
#     end_date = request.GET.get('end_date')
#     search = request.GET.get('search')

#     if category_id:
#         events = events.filter(category_id=category_id)

#     if start_date and end_date:
#         events = events.filter(date__range=[start_date, end_date])

#     if search:
#         events = events.filter(Q(name__icontains=search) | Q(location__icontains=search))

#     return render(request, 'events/event_list.html', {'events': events, 'categories': Category.objects.all()})


# def event_create(request):
#     if request.method == 'POST':
#         form = EventForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('event_list')
#     else:
#         form = EventForm()
#     return render(request, 'events/event_form.html', {'form': form})


# def event_update(request, pk):
#     event = get_object_or_404(Event, pk=pk)
#     if request.method == 'POST':
#         form = EventForm(request.POST, instance=event)
#         if form.is_valid():
#             form.save()
#             return redirect('event_list')
#     else:
#         form = EventForm(instance=event)
#     return render(request, 'events/event_form.html', {'form': form})


# def event_delete(request, pk):
#     event = get_object_or_404(Event, pk=pk)
#     if request.method == 'POST':
#         event.delete()
#         return redirect('event_list')
#     return render(request, 'events/event_confirm_delete.html', {'event': event})


# # # ---------------------------
# # # Participant Views
# # # ---------------------------

# def participant_list(request):
#     #participants = Participant.objects.prefetch_related('events')
#     participants = User.objects.prefetch_related('rsvp_events')
#     return render(request, 'participants/participant_list.html', {'participants': participants})


# def participant_create(request):
#     if request.method == 'POST':
#         form = ParticipantForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('participant_list')
#     else:
#         form = ParticipantForm()
#     return render(request, 'participants/participant_form.html', {'form': form})


# def participant_update(request, pk):
#     participant = get_object_or_404(Participant, pk=pk)
#     if request.method == 'POST':
#         form = ParticipantForm(request.POST, instance=participant)
#         if form.is_valid():
#             form.save()
#             return redirect('participant_list')
#     else:
#         form = ParticipantForm(instance=participant)
#     return render(request, 'participants/participant_form.html', {'form': form})


# def participant_delete(request, pk):
#     participant = get_object_or_404(Participant, pk=pk)
#     if request.method == 'POST':
#         participant.delete()
#         return redirect('participant_list')
#     return render(request, 'participants/participant_confirm_delete.html', {'participant': participant})


# # # ---------------------------
# # # Category Views
# # # ---------------------------

# def category_list(request):
#     categories = Category.objects.all()
#     return render(request, 'categories/category_list.html', {'categories': categories})


# def category_create(request):
#     if request.method == 'POST':
#         form = CategoryForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('category_list')
#     else:
#         form = CategoryForm()
#     return render(request, 'categories/category_form.html', {'form': form})


# def category_update(request, pk):
#     category = get_object_or_404(Category, pk=pk)
#     if request.method == 'POST':
#         form = CategoryForm(request.POST, instance=category)
#         if form.is_valid():
#             form.save()
#             return redirect('category_list')
#     else:
#         form = CategoryForm(instance=category)
#     return render(request, 'categories/category_form.html', {'form': form})


# def category_delete(request, pk):
#     category = get_object_or_404(Category, pk=pk)
#     if request.method == 'POST':
#         category.delete()
#         return redirect('category_list')
#     return render(request, 'categories/category_confirm_delete.html', {'category': category})


# # ---------------------------
# # Stats/Aggregation View
# # ---------------------------

# def dashboard(request):
#     today = timezone.now().date()
#     filter_type = request.GET.get('filter', 'today')

#     total_events = Event.objects.count()
#     upcoming_events = Event.objects.filter(date__gt=today).count()
#     past_events = Event.objects.filter(date__lt=today).count()
#     total_participants = Participant.objects.count()

#     # Filtering logic for below-the-cards event list
#     if filter_type == 'upcoming':
#         filtered_events = Event.objects.filter(date__gt=today).order_by('date')
#     elif filter_type == 'past':
#         filtered_events = Event.objects.filter(date__lt=today).order_by('-date')
#     elif filter_type == 'all':
#         filtered_events = Event.objects.all().order_by('date')
#     elif filter_type == 'participants':
#         filtered_events = []  # Optionally, show participant details instead
#     else:  # default to today's events
#         filtered_events = Event.objects.filter(date=today).order_by('time')

#     return render(request, 'dashboard.html', {
#         'total_events': total_events,
#         'upcoming_events': upcoming_events,
#         'past_events': past_events,
#         'total_participants': total_participants,
#         'filtered_events': filtered_events,
#         'filter': filter_type
#     })
