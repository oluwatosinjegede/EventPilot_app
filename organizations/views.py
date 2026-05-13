from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .forms import OrganizationForm
from .models import Membership, Organization

@login_required
def organization_list(request):
    if Membership.objects.filter(user=request.user, role=Membership.VENDOR).exists() and not Membership.objects.exclude(role=Membership.VENDOR).filter(user=request.user).exists():
        messages.error(request, 'Vendor accounts cannot manage organization settings.')
        return redirect('vendor_dashboard')
    orgs = Organization.objects.filter(memberships__user=request.user).exclude(memberships__user=request.user, memberships__role=Membership.VENDOR).distinct()
    form = OrganizationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        org = form.save(commit=False); org.created_by=request.user; org.save()
        Membership.objects.create(organization=org, user=request.user, role=Membership.OWNER)
        messages.success(request, 'Organization created.')
        return redirect('organizations')
    return render(request, 'organizations/list.html', {'orgs':orgs,'form':form})

@login_required
def organization_detail(request, pk):
    org = get_object_or_404(Organization.objects.exclude(memberships__user=request.user, memberships__role=Membership.VENDOR), pk=pk, memberships__user=request.user)
    return render(request, 'organizations/detail.html', {'org':org})