from django.conf import settings
from django.db import models

class EventTask(models.Model):
    NOT_STARTED='not_started'; IN_PROGRESS='in_progress'; WAITING='waiting'; BLOCKED='blocked'; COMPLETE='complete'
    STATUS_CHOICES=[(NOT_STARTED,'Not started'),(IN_PROGRESS,'In progress'),(WAITING,'Waiting'),(BLOCKED,'Blocked'),(COMPLETE,'Complete')]
    PRIORITY_CHOICES=[('low','Low'),('medium','Medium'),('high','High'),('urgent','Urgent')]
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=NOT_STARTED)
    dependency = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    def __str__(self): return self.title