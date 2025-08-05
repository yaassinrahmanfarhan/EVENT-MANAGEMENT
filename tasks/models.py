from django.db import models

class Event(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200)
    description = models.TextField()
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Participant(models.Model):
    name = models.CharField(max_length=200)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="participants")

    def __str__(self):
        return self.name
