from django.apps import AppConfig

class TasksConfig(AppConfig):
    name = 'tasks'

    def ready(self):
        from django.contrib.auth.models import Group
        groups = ['Admin', 'Organizer', 'Participant']
        for g in groups:
            Group.objects.get_or_create(name=g)
        import tasks.signals

