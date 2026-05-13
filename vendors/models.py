from django.conf import settings
from django.db import models

class Vendor(models.Model):
    STATUS_CHOICES=[('researching','Researching'),('contacted','Contacted'),('quote_received','Quote received'),('selected','Selected'),('contract_sent','Contract sent'),('confirmed','Confirmed'),('paid','Paid'),('completed','Completed')]
    PAYMENT_CHOICES=[('unpaid','Unpaid'),('deposit_paid','Deposit paid'),('paid','Paid'),('overdue','Overdue')]
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='vendors')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='vendor_accounts')
    vendor_name = models.CharField(max_length=200)
    service_type = models.CharField(max_length=120)
    contact_person = models.CharField(max_length=160, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    website = models.URLField(blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='researching')
    payment_status = models.CharField(max_length=30, choices=PAYMENT_CHOICES, default='unpaid')
    notes = models.TextField(blank=True)

    @property
    def company_name(self):
        return self.vendor_name

    @property
    def name(self):
        return self.vendor_name

    @property
    def contact_name(self):
        return self.contact_person

    def __str__(self): return self.vendor_name


class VendorProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendor_profiles')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='profiles')
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='vendor_profiles')
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='vendor_profiles')
    company_name = models.CharField(max_length=200)
    service_type = models.CharField(max_length=120)
    phone = models.CharField(max_length=40, blank=True)
    website = models.URLField(blank=True)
    approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('user', 'event')]

    def __str__(self):
        return f'{self.company_name} — {self.event}'
