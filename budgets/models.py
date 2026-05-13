from django.db import models

class BudgetItem(models.Model):
    PAYMENT_CHOICES=[('unpaid','Unpaid'),('scheduled','Scheduled'),('deposit_paid','Deposit paid'),('paid','Paid'),('overdue','Overdue')]
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='budget_items')
    category = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    actual_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=30, choices=PAYMENT_CHOICES, default='unpaid')
    vendor = models.ForeignKey('vendors.Vendor', null=True, blank=True, on_delete=models.SET_NULL)
    due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    def __str__(self): return self.name