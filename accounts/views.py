from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.shortcuts import redirect, render
from django.urls import reverse_lazy


def register(request):
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Welcome to EventPilot. Create your first organization to get started.')
        return redirect('organizations')
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    form = UserChangeForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save(); messages.success(request, 'Profile updated.'); return redirect('profile')
    return render(request, 'accounts/profile.html', {'form': form})

class EventPilotLoginView(LoginView):
    def get_success_url(self):
        user = self.request.user
        if getattr(user, 'vendor_profiles', None) and user.vendor_profiles.filter(approved=True).exists():
            return reverse_lazy('vendor_dashboard')
        return super().get_success_url()
