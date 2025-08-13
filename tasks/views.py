from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.decorators import login_required
from .models import Event, Category,UserProfile
from .forms import EventForm, UserRegisterForm, CategoryForm, GroupForm,CustomPasswordChangeForm,CustomPasswordResetForm,CustomPasswordResetConfirmForm,EditProfileForm
from django.contrib.auth.forms import AuthenticationForm
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.models import Group
from django.http import HttpResponseForbidden
from django.urls import reverse
from .decorators import role_required
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth import logout
from .forms import CustomLoginForm
from django.utils.timezone import now,localdate
from django.views.generic import TemplateView, ListView, UpdateView, DetailView
from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib.auth.views import LoginView, PasswordChangeView,PasswordResetView,PasswordResetConfirmView
from datetime import date

def Home_page(request):
    query = request.GET.get('q')
    events = Event.objects.prefetch_related('participant')

    if query:
        events = events.filter(name__icontains=query)

    return render(request, 'Home_page.html', {'events': events, 'query': query})


# def Event_details_view(request, event_id):
#     event = get_object_or_404(Event, id=event_id)
#     return render(request, 'Event_details.html', {'event': event})

class Event_details_view(DetailView):
    model = Event
    template_name = 'Event_details.html'
    context_object_name = 'event'
    pk_url_kwarg = 'event_id'

# def Contact_us_view(request):
#     return render(request, 'Contact_us.html')

class Contact_us_view(TemplateView):
    template_name = 'Contact_us.html'


# def About_us_view(request):
#     return render(request, 'About_us.html')

class About_us_view(TemplateView):
    template_name = 'About_us.html'


# def Services_view(request):
#     return render(request, 'Services.html')

class Services_view(TemplateView):
    template_name = 'Services.html'


def dashboard(request):
    today = timezone.now().date()
    filter_type = request.GET.get('filter', 'today')

    total_events = Event.objects.count()
    upcoming_events = Event.objects.filter(date__gt=today).count()
    past_events = Event.objects.filter(date__lt=today).count()
    total_participants = User.objects.filter(rsvp_events__isnull=False).distinct().count()

    if filter_type == 'upcoming':
        filtered_events = Event.objects.filter(date__gt=today).order_by('date')
    elif filter_type == 'past':
        filtered_events = Event.objects.filter(date__lt=today).order_by('-date')
    elif filter_type == 'all':
        filtered_events = Event.objects.all().order_by('date')
    elif filter_type == 'participants':
        filtered_events = []
    else:
        filtered_events = Event.objects.filter(date=today).order_by('time')

    return render(request, 'dashboard.html', {
        'total_events': total_events,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'total_participants': total_participants,
        'filtered_events': filtered_events,
        'filter': filter_type
    })


# def event_list(request):
#     events = Event.objects.select_related('category').prefetch_related('participant')

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

#     return render(request, 'events/event_list.html', {
#         'events': events,
#         'categories': Category.objects.all()
#     })

class event_list(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        events = Event.objects.select_related('category').prefetch_related('participant')
        category_id = self.request.GET.get('category')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        search = self.request.GET.get('search')

        if category_id:
            events = events.filter(category_id=category_id)
        if start_date and end_date:
            events = events.filter(date__range=[start_date, end_date])
        if search:
            events = events.filter(Q(name__icontains=search) | Q(location__icontains=search))

        return events

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

@login_required
@role_required('Admin', 'Organizer')
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            form.save_m2m()
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form})

@login_required
@role_required('Admin', 'Organizer')
def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if event.organizer != request.user:
        return redirect('event_list')

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_list')
    else:
        form = EventForm(instance=event)
    return render(request, 'events/event_form.html', {'form': form})


@role_required('Admin', 'Organizer')
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if event.organizer != request.user:
        return redirect('event_list')

    if request.method == 'POST':
        event.delete()
        return redirect('event_list')
    return render(request, 'events/event_confirm_delete.html', {'event': event})


@login_required
def rsvp_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Only people in Participant group can RSVP
    if not request.user.groups.filter(name='Participant').exists():
        return HttpResponseForbidden("Only participants can RSVP to events.")

    if event.participant.filter(pk=request.user.pk).exists():
        messages.warning(request, "You have already RSVP'd to this event.")
    else:
        event.participant.add(request.user)  # triggers m2m_changed signal to send email
        messages.success(request, "RSVP successful. Confirmation email sent.")
    return redirect('event_details', event_id=event.id)

@login_required
def cancel_rsvp_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if event.participant.filter(pk=request.user.pk).exists():
        event.participant.remove(request.user)
        messages.success(request, "Your RSVP has been canceled.")
    else:
        messages.warning(request, "You had not RSVP'd to this event.")
    return redirect('event_details', event_id=event.id)

# @login_required
# @role_required('Admin')
# def participant_list(request):
#     participants = User.objects.prefetch_related('rsvp_events')
#     return render(request, 'participants/participant_list.html', {'participants': participants})

@method_decorator(login_required, name='dispatch')
@method_decorator(role_required('Admin'), name='dispatch')
class participant_list(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'participants/participant_list.html'
    context_object_name = 'participants'

    def get_queryset(self):
        return User.objects.prefetch_related('rsvp_events')

    def test_func(self):
        return self.request.user.groups.filter(name='Admin').exists()


@login_required
@role_required('Admin')
def participant_create(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # require email activation
            user.save()
            participant_group, _ = Group.objects.get_or_create(name='Participant')
            user.groups.add(participant_group)
            messages.info(request, 'Participant created. An activation email has been sent.')
            return redirect('participant_list')
    else:
        form = UserRegisterForm()
    return render(request, 'participants/participant_form.html', {'form': form})

@login_required
@role_required('Admin')
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

@login_required
@role_required('Admin')
def participant_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        return redirect('participant_list')
    return render(request, 'participants/participant_confirm_delete.html', {'participant': user})


# def category_list(request):
#     categories = Category.objects.all()
#     return render(request, 'categories/category_list.html', {'categories': categories})

class category_list(ListView):
    model = Category
    template_name = 'categories/category_list.html'
    context_object_name = 'categories'

@login_required
@role_required('Admin', 'Organizer')
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'categories/category_form.html', {'form': form})

@login_required
@role_required('Admin', 'Organizer')
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

@login_required
@role_required('Admin', 'Organizer')
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'categories/category_confirm_delete.html', {'category': category})


#update


def activate_account(request, user_id, token):
    try:
        user = User.objects.get(id=user_id)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()

            messages.success(request, 'Your account has been activated. You can now log in.')
            return redirect('login')

        else:
            return HttpResponse('Invalid Id or token')

    except User.DoesNotExist:
        return HttpResponse('User not found')

def signup_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # mark inactive until activation
            user.is_active = False
            user.save()
            # assign Participant group (default)
            participant_group, _ = Group.objects.get_or_create(name='Participant')
            user.groups.add(participant_group)
            # signals will send activation email (post_save)
            messages.info(request, 'Registration successful. Please check your email to activate your account.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'participants/participant_form.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = CustomLoginForm

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_active:
            messages.error(self.request, "Your account is not active. Please check your email for the activation link.")
            return redirect('login')
        login(self.request, user)
        return redirect(self.get_success_url())

    def get_success_url(self):
        user = self.request.user
        if user.groups.filter(name='Admin').exists():
            return reverse('admin_dashboard')
        if user.groups.filter(name='Organizer').exists():
            return reverse('organizer_dashboard')
        return reverse('participant_dashboard')
    
@login_required
@role_required('Admin')
@login_required
@role_required('Admin')
def admin_dashboard(request):
    is_admin = request.user.groups.filter(name='Admin').exists()

    events = Event.objects.prefetch_related('participant').all()

    # --- Event categorization ---
    today = localdate()  # use local date instead of timezone.now().date()
    past_events = events.filter(date__lt=today).order_by('-date')
    todays_events = events.filter(date=today).order_by('date')
    upcoming_events = events.filter(date__gt=today).order_by('date')

    # Unique participants across all events
    total_participants = User.objects.filter(
        id__in=Event.objects.values_list('participant', flat=True)
    ).distinct().count()

    participants = User.objects.filter(rsvp_events__isnull=False).distinct()
    categories = Category.objects.all()

    total_events = events.count()
    total_organizers = User.objects.filter(groups__name='Organizer').count()

    # Recent participants
    recent_participants = []
    for event in events:
        for user in event.participant.all():
            recent_participants.append({
                'username': user.username,
                'email': user.email,
                'event_name': event.name,
                'date_joined': event.created_at
            })
    recent_participants = sorted(
        recent_participants,
        key=lambda x: x['date_joined'],
        reverse=True
    )[:5]

    return render(
        request,
        'dashboards/admin_dashboard.html',
        {
            'events': events,
            'past_events': past_events,
            'todays_events': todays_events,
            'upcoming_events': upcoming_events,
            'participants': participants,
            'categories': categories,
            'is_admin': is_admin,
            'total_events': total_events,
            'total_participants': total_participants,
            'total_organizers': total_organizers,
            'recent_participants': recent_participants,
        }
    )



@login_required
@role_required('Organizer')
def organizer_dashboard(request):
    is_organizer = request.user.groups.filter(name='Organizer').exists()
    if not is_organizer:
        return HttpResponseForbidden()

    # Show all events (like admin)
    events = Event.objects.prefetch_related('participant').all()
    categories = Category.objects.all()

    today = localdate()  # <-- use localdate() instead of timezone.now().date()
    
    past_events = events.filter(date__lt=today).order_by('-date')
    todays_events = events.filter(date=today).order_by('date')
    upcoming_events = events.filter(date__gt=today).order_by('date')

    total_events = events.count()
    total_participants = sum([e.participant.count() for e in events])

    return render(
        request,
        'dashboards/organizer_dashboard.html',
        {
            'events': events,
            'past_events': past_events,
            'todays_events': todays_events,
            'upcoming_events': upcoming_events,
            'categories': categories,
            'is_organizer': is_organizer,
            'total_events': total_events,
            'total_participants': total_participants,
        }
    )



@login_required
@role_required('Participant')
def participant_dashboard(request):
    user = request.user
    today = now().date()

    registered_events = user.rsvp_events.all().order_by('date')

    total_registered_events = registered_events.count()
    upcoming_events_count = registered_events.filter(date__gte=today).count()

    # Example logic for recommended events (customize as you want)
    # For example: events user is NOT registered for and date in future
    recommended_events = Event.objects.exclude(participant=user).filter(date__gte=today).order_by('date')[:6]

    context = {
        'registered_events': registered_events,
        'total_registered_events': total_registered_events,
        'upcoming_events_count': upcoming_events_count,
        'recommended_events': recommended_events,
        'today': today,
    }
    return render(request, 'dashboards/participant_dashboard.html', context)


# @login_required
# @role_required('Admin')
# def group_list(request):
#     groups = Group.objects.all()
#     return render(request, 'admin/group_list.html', {'groups': groups})

@method_decorator(login_required, name='dispatch')
@method_decorator(role_required('Admin'), name='dispatch')
class group_list(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Group
    template_name = 'admin/group_list.html'
    context_object_name = 'groups'

    def test_func(self):
        return self.request.user.groups.filter(name='Admin').exists()


@login_required
@role_required('Admin')
def group_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.save()
            form.save_m2m()  # Saves the permissions relation
            messages.success(request, "Group created successfully with permissions.")
            return redirect('group_list')
    else:
        form = GroupForm()
    return render(request, 'admin/group_form.html', {'form': form})

@login_required
@role_required('Admin')
def group_update(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, "Group updated successfully.")
            return redirect('group_list')
    else:
        form = GroupForm(instance=group)
    return render(request, 'admin/group_form.html', {'form': form})

@login_required
@role_required('Admin')
def group_delete(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        group.delete()
        messages.success(request, "Group deleted successfully.")
        return redirect('group_list')
    return render(request, 'admin/group_confirm_delete.html', {'group': group})

class LogoutGetView(View):
    def post(self, request):  # Handle POST requests only
        logout(request)
        messages.success(request, "You have been logged out successfully.")
        return redirect('home')  # Redirect after logout

    def get(self, request):  # This could be used for other logic, but POST is recommended for logout.
        return redirect('home')


@login_required
def manage_roles(request):
    if not request.user.groups.filter(name='Admin').exists():
        return HttpResponseForbidden("You do not have permission to access this page.")
    
    users = User.objects.exclude(id=request.user.id)  # Exclude current admin if you want
    
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        new_role = request.POST.get("role")
        
        user = get_object_or_404(User, id=user_id)
        
        # Remove from all role groups first
        user.groups.clear()
        
        # Add to the selected role group
        group = Group.objects.get(name=new_role)
        user.groups.add(group)
        
        return redirect("manage_roles")
    
    return render(request, "admin/manage_roles.html", {"users": users})


class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['username'] = user.username
        context['email'] = user.email
        context['name'] = user.get_full_name()
        context['bio'] = user.userprofile.bio
        context['profile_image'] = user.userprofile.profile_image
        context['phone_number'] = user.userprofile.phone_number

        context['member_since'] = user.date_joined
        context['last_login'] = user.last_login
        return context


class ChangePassword(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = CustomPasswordChangeForm


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('login')
    html_email_template_name = 'registration/reset_email.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['protocol'] = 'https' if self.request.is_secure() else 'http'
        context['domain'] = self.request.get_host()
        print(context)
        return context

    def form_valid(self, form):
        messages.success(
            self.request, 'A Reset email sent. Please check your email')
        return super().form_valid(form)
    

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomPasswordResetConfirmForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(
            self.request, 'Password reset successfully')
        return super().form_valid(form)
    

class EditProfileView(UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'accounts/update_profile.html'
    context_object_name = 'form'

    def get_object(self):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['userprofile'] = UserProfile.objects.get(user=self.request.user)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_profile'] = UserProfile.objects.get(user=self.request.user)
        return context

    def form_valid(self, form):
        form.save(commit=True)
        return redirect('profile')


