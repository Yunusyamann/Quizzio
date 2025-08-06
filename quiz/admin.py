from django.contrib import admin
from .models import GameSession, Player, Question, Choice, Answer

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ('text', 'order')

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    # 'session_id' alanını 'session_code' olarak değiştiriyoruz.
    list_display = ('session_code', 'host', 'is_active', 'created_at')

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'session', 'score')

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')
    
admin.site.register(Answer)