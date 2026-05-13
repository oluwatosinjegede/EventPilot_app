from django.db import models

class Vendor(models.Model):
    STATUS_CHOICES=[('researching','Researching'),('contacted','Contacted'),('quote_received','Quote received'),('selected','Selected'),('contract_sent','Contract sent'),('confirmed','Confirmed'),('paid','Paid'),('completed','Completed')]
    PAYMENT_CHOICES=[('unpaid','Unpaid'),('deposit_paid','Deposit paid'),('paid','Paid'),('overdue','Overdue')]
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='vendors')
    vendor_name = models.CharField(max_length=200)
    service_type = models.CharField(max_length=120)
    contact_person = models.CharField(max_length=160, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    website = models.URLField(blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='researching')
    payment_status = models.CharField(max_length=30, choices=PAYMENT_CHOICES, default='unpaid')
    notes = models.TextField(blank=True)
    def __str__(self): return self.vendor_name
