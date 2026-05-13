from django.conf import settings
from django.db import models
class PromotionTask(models.Model):
    CHANNELS=[('email','Email'),('instagram','Instagram'),('tiktok','TikTok'),('facebook','Facebook'),('posters','Posters'),('school_announcements','School announcements'),('community_boards','Community boards'),('website','Website'),('newsletter','Newsletter')]
    STATUSES=[('not_started','Not started'),('in_progress','In progress'),('blocked','Blocked'),('complete','Complete')]
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='promotion_tasks')
    promotion_channel = models.CharField(max_length=40, choices=CHANNELS)
    content_idea = models.TextField()
    assigned_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUSES, default='not_started')
    asset_upload = models.FileField(upload_to='promotion_assets/', blank=True)
    notes = models.TextField(blank=True)