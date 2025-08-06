import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.db import transaction  # <-- GÜVENLİK İÇİN GEREKLİ İMPORT
from .models import GameSession, Player, Question, Choice, Answer
from .tasks import start_game_countdown

class LobbyConsumer(AsyncJsonWebsocketConsumer):
    """
    Lobi sayfasıyla ilgili WebSocket iletişimini yönetir.
    Oyuncu katılımı, ayrılması ve oyunun başlatılması gibi olayları işler.
    """
    async def connect(self):
        self.session_code = self.scope['url_route']['kwargs']['session_code']
        self.lobby_group_name = f'lobby_{self.session_code}'
        await self.channel_layer.group_add(self.lobby_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.lobby_group_name, self.channel_name)

    async def receive_json(self, content):
        command = content.get('command')
        player_name = content.get('player_name')

        if command == 'join_lobby' and player_name:
            session = await sync_to_async(GameSession.objects.get)(session_code=self.session_code)
            player, created = await sync_to_async(Player.objects.get_or_create)(
                session=session,
                name=player_name,
                defaults={'channel_name': self.channel_name}
            )
            if not created:
                player.channel_name = self.channel_name
                await sync_to_async(player.save)()
            
            await self.broadcast_players()
        
        elif command == 'start_game':
            host_user = self.scope['user']
            session = await sync_to_async(GameSession.objects.select_related('host').get)(session_code=self.session_code)
            if host_user.is_authenticated and session.host == host_user:
                await self.channel_layer.group_send(
                    self.lobby_group_name,
                    {'type': 'game.start'}
                )

    async def broadcast_players(self):
        session = await sync_to_async(GameSession.objects.get)(session_code=self.session_code)
        players = await sync_to_async(list)(session.players.values('name'))
        await self.channel_layer.group_send(
            self.lobby_group_name,
            {
                'type': 'player.update',
                'players': players
            }
        )

    async def player_update(self, event):
        await self.send_json(event)

    async def game_start(self, event):
        await self.send_json(event)


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """
    Kullanıcıya özel bildirimleri göndermek için kullanılır.
    Örn: "Yapay zeka soruları oluşturmayı tamamladı."
    """
    async def connect(self):
        user = self.scope.get("user")
        if user and user.is_authenticated:
            self.group_name = f"user_{user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notification(self, event):
        await self.send_json({
            'type': 'notification',
            'message': event['message'],
            'status': event.get('status', 'info')
        })


#--- GameConsumer (ÇİFT TETİKLEME SORUNU İÇİN DÜZELTİLMİŞ HALİ) ---
class GameConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.session_code = self.scope['url_route']['kwargs']['session_code']
        self.player_name = self.scope['url_route']['kwargs']['player_name']
        self.game_group_name = f'game_{self.session_code}'

        await self.channel_layer.group_add(
            self.game_group_name,
            self.channel_name
        )
        await self.accept()

        user = self.scope.get("user")
        if user and user.is_authenticated:
            # Sadece host'un oyunu başlatabilmesini sağlayan güvenli metodu çağır
            await self.trigger_game_start(user)

    @sync_to_async
    def trigger_game_start(self, user):
        """
        Veritabanı kilitleme mekanizması kullanarak oyunun SADECE BİR KEZ
        başlatılmasını garanti eden metot.
        """
        try:
            with transaction.atomic():
                session = GameSession.objects.select_for_update().get(session_code=self.session_code)
                if session.host == user and not session.game_started:
                    session.game_started = True
                    session.save()
                    print(f"Oyun {self.session_code} host tarafından başlatılıyor...")
                    start_game_countdown.delay(self.session_code)
        except GameSession.DoesNotExist:
            print(f"Oyun başlatma hatası: Oturum {self.session_code} bulunamadı.")
            pass

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.game_group_name,
            self.channel_name
        )

    async def receive_json(self, content):
        command = content.get('command')
        if command == 'submit_answer':
            await self.save_answer(content)
    
    async def save_answer(self, data):
        await sync_to_async(self._save_answer_sync)(data)

    def _save_answer_sync(self, data):
        try:
            session = GameSession.objects.get(session_code=self.session_code)
            player = Player.objects.get(name=self.player_name, session=session)
            question = Question.objects.get(id=data['question_id'])
            if Answer.objects.filter(player=player, question=question).exists():
                return
            selected_choice = Choice.objects.get(id=data['choice_id'])
            is_correct = selected_choice.is_correct
            if is_correct:
                player.score += 10
                player.save(update_fields=['score'])
            Answer.objects.create(player=player, question=question, selected_choice=selected_choice, is_correct=is_correct)
        except (GameSession.DoesNotExist, Player.DoesNotExist, Question.DoesNotExist, Choice.DoesNotExist) as e:
            print(f"HATA: Cevap kaydedilemedi. Detay: {e}")

    async def game_countdown(self, event):
        await self.send_json(event)
        
    async def new_question(self, event):
        await self.send_json(event)

    async def show_scoreboard(self, event):
        await self.send_json(event)