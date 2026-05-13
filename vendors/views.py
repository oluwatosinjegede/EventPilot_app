from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from notifications.models import NotificationLog
from organizations.models import Membership
from timelines.models import EventTask
from .forms import VendorProfileForm, VendorRegistrationForm
from .models import Vendor, VendorProfile


def is_vendor_user(user):
    return user.is_authenticated and VendorProfile.objects.filter(user=user, approved=True).exists()


def vendor_events_for_user(user):
    return VendorProfile.objects.filter(user=user, approved=True).select_related('vendor', 'organization', 'event')


@transaction.atomic
def _create_vendor_account(form):
    user = form.save(commit=False)
    user.username = form.cleaned_data['email'].strip().lower()[:150]
    user.email = form.cleaned_data['email'].strip().lower()
    full_name = form.cleaned_data['full_name'].strip()
    first, _, last = full_name.partition(' ')
    user.first_name = first
    user.last_name = last
    user.save()

    event = form.cleaned_data['event']
    organization = form.cleaned_data['organization']
    email = user.email
    vendor = Vendor.objects.filter(event=event, email__iexact=email).first()
    if vendor:
        vendor.user = user
        vendor.vendor_name = vendor.vendor_name or form.cleaned_data['company_name']
        vendor.service_type = vendor.service_type or form.cleaned_data['service_type']
        vendor.contact_person = vendor.contact_person or full_name
        vendor.phone = vendor.phone or form.cleaned_data.get('phone', '')
        vendor.website = vendor.website or form.cleaned_data.get('website', '')
        vendor.status = 'confirmed'
        vendor.save()
    else:
        vendor = Vendor.objects.create(
            event=event,
            user=user,
            vendor_name=form.cleaned_data['company_name'],
            service_type=form.cleaned_data['service_type'],
            contact_person=full_name,
            email=email,
            phone=form.cleaned_data.get('phone', ''),
            website=form.cleaned_data.get('website', ''),
            status='confirmed',
        )

    Membership.objects.get_or_create(organization=organization, user=user, defaults={'role': Membership.VENDOR})
    profile, _ = VendorProfile.objects.update_or_create(
        user=user,
        event=event,
        defaults={
            'vendor': vendor,
            'organization': organization,
            'company_name': form.cleaned_data['company_name'],
            'service_type': form.cleaned_data['service_type'],
            'phone': form.cleaned_data.get('phone', ''),
            'website': form.cleaned_data.get('website', ''),
            'approved': True,
        },
    )
    return user, profile


def register(request):
    form = VendorRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user, profile = _create_vendor_account(form)
        login(request, user)
        messages.success(request, f'Welcome, {profile.company_name}. Your vendor account is connected to {profile.event.title}.')
        return redirect('vendor_dashboard')
    return render(request, 'vendors/register.html', {'form': form})


@login_required
def dashboard(request):
    profiles = list(vendor_events_for_user(request.user))
    if not profiles:
        messages.error(request, 'Your account is not connected to an approved vendor profile.')
        return redirect('dashboard')
    vendor_ids = [profile.vendor_id for profile in profiles]
    event_ids = [profile.event_id for profile in profiles]
    notifications = NotificationLog.objects.filter(vendor_id__in=vendor_ids, event_id__in=event_ids).select_related('event', 'guest')[:50]
    tasks = EventTask.objects.filter(event_id__in=event_ids, assigned_user=request.user).select_related('event').order_by('due_date', 'priority')[:50]
    return render(request, 'vendors/dashboard.html', {'profiles': profiles, 'notifications': notifications, 'tasks': tasks})


@login_required
def profile(request):
    profile = vendor_events_for_user(request.user).first()
    if not profile:
        messages.error(request, 'Your account is not connected to an approved vendor profile.')
        return redirect('dashboard')
    form = VendorProfileForm(request.POST or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        profile = form.save()
        vendor = profile.vendor
        vendor.vendor_name = profile.company_name
        vendor.service_type = profile.service_type
        vendor.phone = profile.phone
        vendor.website = profile.website
        vendor.save(update_fields=['vendor_name', 'service_type', 'phone', 'website'])
        messages.success(request, 'Vendor profile updated.')
        return redirect('vendor_profile')
    return render(request, 'vendors/profile.html', {'form': form, 'profile': profile})


@login_required
def approve(request, event_id, vendor_id):
    vendor = get_object_or_404(Vendor, pk=vendor_id, event_id=event_id)
    vendor.profiles.update(approved=True)
    vendor.status = 'confirmed'
    vendor.save(update_fields=['status'])
    messages.success(request, f'{vendor.vendor_name} approved.')
    return redirect('event_vendors', event_id)


@login_required
def reject(request, event_id, vendor_id):
    vendor = get_object_or_404(Vendor, pk=vendor_id, event_id=event_id)
    vendor.profiles.update(approved=False)
    vendor.status = 'researching'
    vendor.save(update_fields=['status'])
    messages.warning(request, f'{vendor.vendor_name} rejected.')
    return redirect('event_vendors', event_id)
