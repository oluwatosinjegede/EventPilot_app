import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from events.models import Event
from invitations.services import validate_qr_token


def api_validate_check_in(request, event_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    event=get_object_or_404(Event, pk=event_id)
    if request.content_type == 'application/json':
        try:
            data=json.loads(request.body.decode('utf-8') or '{}')
        except json.JSONDecodeError:
            data={}
    else:
        data=request.POST
    token=data.get('qr_token') or data.get('access_code') or ''
    result=validate_qr_token(token, event, request.user if request.user.is_authenticated else None)
    status_code=200 if result['status'] in {'valid','already_checked_in'} else 400
    return JsonResponse({
        'status': result['status'],
        'message': result['message'],
        'guest': result['guest'].full_name if result['guest'] else None,
        'checked_in_at': result['guest'].checked_in_at.isoformat() if result['guest'] and result['guest'].checked_in_at else None,
    }, status=status_code)