# EventPilot

EventPilot is a functional Django SaaS application for planning, organizing, and executing events. It includes organization-scoped event management, guest invitations, RSVP preferences, QR-code digital access cards, check-in auditing, vendor notifications, budgeting, logistics, schedules, promotion tasks, contingency planning, and reports.

## Stack

- Backend: Django
- Frontend: Django HTML templates with Tailwind CSS CDN
- Database: SQLite for development
- Email: Django console email backend
- QR codes: `qrcode[pil]`
- Excel imports: `openpyxl`

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate --run-syncdb
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000, register, create an organization, then create your first event.

## Core flows

1. Register or log in.
2. Create an organization.
3. Create an event.
4. Add guests manually, via bulk text, CSV, or Excel.
5. Send invitations from the guest page. Development emails print invite URLs to the console.
6. Guests RSVP publicly at `/invite/<token>/` and submit preferences.
7. Confirmed guests receive QR-based digital access cards at `/access-card/<access_code>/`.
8. Staff check guests in at `/events/<id>/check-in/` with duplicate prevention and audit logs.
9. Vendor notification rules can email selected guest confirmation and arrival details.

## Import columns

Guest CSV/Excel imports require a `full_name` column. Optional columns include `email`, `phone`, `group_name`, `access_type`, and `notes`.
