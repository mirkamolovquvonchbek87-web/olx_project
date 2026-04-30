from django.db import models
from django.conf import settings
from apps.models.base import CreatedBaseModel

class Transaction(CreatedBaseModel):
    class Type(models.TextChoices):
        DEPOSIT = 'deposit', 'Пополнение'
        PURCHASE = 'purchase', 'Покупка'
        REFUND = 'refund', 'Возврат'
        BONUS = 'bonus', 'Бонус'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидание'
        SUCCESS = 'success', 'Успешно'
        FAILED = 'failed', 'Ошибка'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=Type.choices, default=Type.PURCHASE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUCCESS)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'

    def __str__(self):
        return f"{self.user.username} - {self.amount} ({self.get_transaction_type_display()})"
