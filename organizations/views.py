from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .forms import OrganizationForm
from .models import Membership, Organization

@login_required
def organization_list(request):
    orgs = Organization.objects.filter(memberships__user=request.user).distinct()
    form = OrganizationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        org = form.save(commit=False); org.created_by=request.user; org.save()
        Membership.objects.create(organization=org, user=request.user, role=Membership.OWNER)
        messages.success(request, 'Organization created.')
        return redirect('organizations')
    return render(request, 'organizations/list.html', {'orgs':orgs,'form':form})

@login_required
def organization_detail(request, pk):
    org = get_object_or_404(Organization, pk=pk, memberships__user=request.user)
    return render(request, 'organizations/detail.html', {'org':org})