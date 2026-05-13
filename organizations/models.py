from django.conf import settings
from django.db import models
from event_codes import generate_unique_code

class Organization(models.Model):
    name = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    organization_code = models.CharField(max_length=10, unique=True, db_index=True, editable=False, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_organizations')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.organization_code:
            self.organization_code = generate_unique_code(Organization, 'organization_code', 'ORG')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Membership(models.Model):
    OWNER = 'owner'; ADMIN = 'admin'; PLANNER = 'planner'; STAFF = 'staff'; VOLUNTEER = 'volunteer'; VENDOR = 'vendor'; VIEWER = 'viewer'
    ROLE_CHOICES = [(OWNER,'Owner'),(ADMIN,'Admin'),(PLANNER,'Planner'),(STAFF,'Staff'),(VOLUNTEER,'Volunteer'),(VENDOR,'Vendor'),(VIEWER,'Viewer')]
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=PLANNER)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('organization', 'user')]

    def __str__(self):
        return f'{self.user} — {self.organization} ({self.role})'
