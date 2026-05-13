import secrets
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import models

class DigitalAccessCard(models.Model):
    guest = models.OneToOneField('guests.Guest', on_delete=models.CASCADE, related_name='access_card')
    access_code = models.CharField(max_length=48, unique=True, default=lambda: secrets.token_urlsafe(18))
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
    active = models.BooleanField(default=True)
    confirmation_status = models.CharField(max_length=40, default='confirmed')
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self,*args,**kwargs):
        super().save(*args,**kwargs)
        if not self.qr_code:
            import qrcode
            img = qrcode.make(self.access_code)
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            self.qr_code.save(f'{self.access_code}.png', ContentFile(buffer.getvalue()), save=False)
            super().save(update_fields=['qr_code'])
    def __str__(self): return self.access_code
