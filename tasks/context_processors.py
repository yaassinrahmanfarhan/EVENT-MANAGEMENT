def user_roles(request):
    is_admin = request.user.is_authenticated and request.user.groups.filter(name='Admin').exists()
    is_organizer = request.user.is_authenticated and request.user.groups.filter(name='Organizer').exists()
    is_participant = request.user.is_authenticated and request.user.groups.filter(name='Participant').exists()
    
    return {
        'is_admin': is_admin,
        'is_organizer': is_organizer,
        'is_participant': is_participant
    }