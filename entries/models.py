from django.conf import settings
from django.db import models
from django.urls import reverse


class Mood(models.TextChoices):
    """Варианты настроения, которое пользователь может указать в записи."""
    GREAT = "great", "😄 Отлично"
    GOOD = "good", "🙂 Хорошо"
    NEUTRAL = "neutral", "😐 Нормально"
    SAD = "sad", "😢 Грустно"
    ANXIOUS = "anxious", "😰 Тревожно"
    ANGRY = "angry", "😠 Злюсь"


class Entry(models.Model):
    """Запись личного дневника, принадлежащая одному пользователю."""
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="entries",
        verbose_name="Автор",
    )
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержимое")
    mood = models.CharField(
        max_length=10,
        choices=Mood.choices,
        default=Mood.NEUTRAL,
        verbose_name="Настроение",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Изменена")

    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("entries:detail", kwargs={"pk": self.pk})
