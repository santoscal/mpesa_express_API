from django.db import models

class AccTopUp(models.Model):
    phone = models.CharField(max_length=10, null=False, blank=False)
    amount = models.DecimalField(max_digits=100, decimal_places=2, null=False, blank=False)

    class Meta:
        app_label = 'sbs_mpesa'

    def __str__(self):
        return f"Phone: {self.phone}, Amount: {self.amount}"
