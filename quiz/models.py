# quiz/models.py
from django.db import models
from django.contrib.auth.models import User
import uuid
import random
import string
def generate_unique_code():
    """4 haneli, benzersiz bir oyun kodu üretir."""
    length = 4
    while True:
        # 4 haneli rastgele bir kod oluştur (Büyük Harf ve Rakamlardan)
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        # Bu kodun daha önce kullanılıp kullanılmadığını kontrol et
        if GameSession.objects.filter(session_code=code).count() == 0:
            break
    return code
class GameSession(models.Model):
    # session_id'yi session_code ile değiştirdik
    session_code = models.CharField(max_length=4, primary_key=True, default=generate_unique_code, editable=False)
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    current_question_index = models.IntegerField(default=0)
    game_started = models.BooleanField(default=False)

    def __str__(self):
        return f"Oda: {self.session_code} - Host: {self.host.username}"

class Player(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    # 'session' ilişkisini yeni primary key alanımıza göre güncelliyoruz.
    session = models.ForeignKey(GameSession, related_name='players', on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    channel_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.name} (Oda: {self.session.session_code})"

class Question(models.Model):
    text = models.TextField()
    order = models.IntegerField(help_text="Sorunun gösterilme sırası")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Soru {self.order}: {self.text[:30]}..."

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Doğru' if self.is_correct else 'Yanlış'})"

class Answer(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.name} -> {self.question.text[:20]}..."