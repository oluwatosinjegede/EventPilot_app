from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from accounts import views as account_views
from events import views as event_views
from invitations import views as invitation_views
from access import views as access_views
from checkins import views as checkin_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', event_views.home, name='home'),
    path('dashboard/', event_views.dashboard, name='dashboard'),
    path('accounts/register/', account_views.register, name='register'),
    path('accounts/profile/', account_views.profile, name='profile'),
    path('accounts/login/', account_views.EventPilotLoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('accounts/password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('organizations/', include('organizations.urls')),
    path('vendors/', include('vendors.urls')),
    path('events/', include('events.urls')),
    path('invite/<str:token>/', invitation_views.invite_rsvp, name='invite_rsvp'),
    path('access-card/<str:access_code>/', access_views.access_card, name='access_card'),
    path('api/events/<int:event_id>/send-invites/', invitation_views.api_send_invites, name='api_send_invites'),
    path('api/invites/<str:token>/', invitation_views.api_invite_details, name='api_invite_details'),
    path('api/invites/<str:token>/rsvp/', invitation_views.api_submit_rsvp, name='api_submit_rsvp'),
    path('api/invites/<str:token>/menu/', invitation_views.api_menu_selection, name='api_menu_selection'),
    path('api/invites/<str:token>/seat/', invitation_views.api_seat_selection, name='api_seat_selection'),
    path('api/guests/<int:guest_id>/resend-access-card/', invitation_views.api_resend_access_card, name='api_resend_access_card'),
    path('api/events/<int:event_id>/check-in/', checkin_views.api_validate_check_in, name='api_validate_check_in'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
