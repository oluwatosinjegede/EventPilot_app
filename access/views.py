from django.shortcuts import get_object_or_404, render
from .models import DigitalAccessCard

def access_card(request, access_code):
    card=get_object_or_404(DigitalAccessCard.objects.select_related('guest__event'), access_code=access_code)
    return render(request,'access/card.html', {'card':card,'guest':card.guest,'event':card.guest.event})