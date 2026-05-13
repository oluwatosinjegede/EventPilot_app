from django import forms
from events.models import Event
from timelines.models import EventTask
from budgets.models import BudgetItem
from vendors.models import Vendor
from guests.models import Guest
from logistics.models import LogisticsPlan
from schedules.models import ScheduleItem
from promotions.models import PromotionTask
from contingencies.models import ContingencyPlan
from notifications.models import VendorNotificationRule

class TailwindMixin:
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault('class','w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500')

class EventForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model=Event; exclude=['organization']
        widgets={'start_at':forms.DateTimeInput(attrs={'type':'datetime-local'}),'end_at':forms.DateTimeInput(attrs={'type':'datetime-local'}),'description':forms.Textarea(attrs={'rows':3}),'venue_address':forms.Textarea(attrs={'rows':2})}
class TaskForm(TailwindMixin, forms.ModelForm):
    class Meta: model=EventTask; exclude=['event']
class BudgetItemForm(TailwindMixin, forms.ModelForm):
    class Meta: model=BudgetItem; exclude=['event']
class VendorForm(TailwindMixin, forms.ModelForm):
    class Meta: model=Vendor; exclude=['event']
class GuestForm(TailwindMixin, forms.ModelForm):
     class Meta: model=Guest; exclude=['event','public_id','invitation_token','invite_status','email_invite_status','whatsapp_invite_status','rsvp_status','rsvp_submitted_at','selected_menu_choice','seat_assignment','invitation_sent_at','invitation_opened_at','rsvp_updated_at','pass_delivery_email_status','pass_delivery_whatsapp_status','checked_in','checked_in_at']
class GuestUploadForm(TailwindMixin, forms.Form):
    file=forms.FileField(help_text='Upload .csv, .xlsx, or .xls with at least full_name plus optional email, phone, group_name, access_type, notes.')
class BulkGuestForm(TailwindMixin, forms.Form):
    guests=forms.CharField(widget=forms.Textarea(attrs={'rows':6}), help_text='One guest per line: Full Name, email, phone')
class LogisticsPlanForm(TailwindMixin, forms.ModelForm):
    class Meta: model=LogisticsPlan; exclude=['event']
class ScheduleItemForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model=ScheduleItem; exclude=['event']
        widgets={'start_time':forms.DateTimeInput(attrs={'type':'datetime-local'}),'end_time':forms.DateTimeInput(attrs={'type':'datetime-local'})}
class PromotionTaskForm(TailwindMixin, forms.ModelForm):
    class Meta: model=PromotionTask; exclude=['event']
class ContingencyPlanForm(TailwindMixin, forms.ModelForm):
    class Meta: model=ContingencyPlan; exclude=['event']
class VendorNotificationRuleForm(TailwindMixin, forms.ModelForm):
    class Meta: model=VendorNotificationRule; exclude=['event']
