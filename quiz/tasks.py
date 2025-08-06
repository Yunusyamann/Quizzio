from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import time
# DÜZELTME: Eksik olan 'Choice' modeli import edildi
from .models import GameSession, Question, Player, Answer, Choice
import google.generativeai as genai
from django.conf import settings
import json

@shared_task
def start_game_countdown(session_code):
    channel_layer = get_channel_layer()
    game_group_name = f'game_{session_code}'

    for i in range(5, 0, -1):
        async_to_sync(channel_layer.group_send)(
            game_group_name,
            {
                'type': 'game.countdown',
                'message': f'Oyun {i} saniye içinde başlıyor...'
            }
        )
        time.sleep(1)
    
    send_next_question.delay(session_code)


@shared_task
def send_next_question(session_code):
    channel_layer = get_channel_layer()
    game_group_name = f'game_{session_code}'
    
    try:
        session = GameSession.objects.get(session_code=session_code, is_active=True)
        all_questions = Question.objects.all().order_by('order')
        total_questions = all_questions.count()
        
        if session.current_question_index < total_questions:
            question = all_questions[session.current_question_index]
            choices = [{'id': choice.id, 'text': choice.text} for choice in question.choices.all()]
            
            question_index = session.current_question_index + 1
            
            async_to_sync(channel_layer.group_send)(
                game_group_name,
                {
                    'type': 'new.question',
                    'question': question.text,
                    'choices': choices,
                    'question_id': question.id,
                    'time_limit': 20,
                    'question_index': question_index,
                    'total_questions': total_questions,
                }
            )
            
            session.current_question_index += 1
            session.save()
            send_next_question.apply_async(args=[session_code], countdown=20)
        else:
            show_scoreboard.delay(session_code)
            
    except GameSession.DoesNotExist:
        print(f"HATA: Oturum bulunamadı: {session_code}")


@shared_task
def show_scoreboard(session_code):
    channel_layer = get_channel_layer()
    game_group_name = f'game_{session_code}'
    
    session = GameSession.objects.get(session_code=session_code)
    players = Player.objects.filter(session=session).order_by('-score')
    
    scoreboard = []
    rank = 1
    for player in players:
        correct_answers = Answer.objects.filter(player=player, is_correct=True).count()
        wrong_answers = Answer.objects.filter(player=player, is_correct=False).count()
        scoreboard.append({
            'rank': rank,
            'name': player.name,
            'score': player.score,
            'correct': correct_answers,
            'wrong': wrong_answers
        })
        rank += 1

    async_to_sync(channel_layer.group_send)(
        game_group_name,
        {
            'type': 'show.scoreboard',
            'scoreboard': scoreboard
        }
    )
    
    session.is_active = False
    session.save()

@shared_task
def generate_questions_from_prompt(user_prompt, user_id):
    channel_layer = get_channel_layer()
    user_group_name = f"user_{user_id}"
    """
    Kullanıcıdan gelen prompt ile Gemini API'yi kullanarak sorular oluşturur
    ve veritabanına kaydeder.
    """
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')

        system_prompt = f"""
        Sen bir bilgi yarışması için soru hazırlayan bir asistansın.
        Sana verilen konuyla ilgili 10 adet çoktan seçmeli soru oluştur.
        Her sorunun 4 şıkkı olmalı ve bu şıklardan sadece biri doğru olmalı.
        Cevabını, başka hiçbir metin olmadan, doğrudan JSON formatında bir liste olarak ver.
        JSON formatı şu şekilde olmalı:
        [
            {{
                "order": 1,
                "text": "Soru metni burada yer alacak",
                "choices": [
                    {{"text": "A şıkkı metni", "is_correct": false}},
                    {{"text": "B şıkkı metni (doğru cevap)", "is_correct": true}},
                    {{"text": "C şıkkı metni", "is_correct": false}},
                    {{"text": "D şıkkı metni", "is_correct": false}}
                ]
            }},
            ... (diğer 9 soru)
        ]
        Kullanıcının istediği konu: "{user_prompt}"
        """

        print("Gemini API'ye istek gönderiliyor...")
        response = model.generate_content(system_prompt)
        
        clean_response = response.text.strip().replace('```json', '').replace('```', '')
        
        questions_data = json.loads(clean_response)
        
        print("Sorular başarıyla oluşturuldu. Veritabanı güncelleniyor...")

        # Mevcut soruları sil
        Choice.objects.all().delete()
        Question.objects.all().delete()

        # Yeni soruları veritabanına kaydet
        for q_data in questions_data:
            question = Question.objects.create(text=q_data['text'], order=q_data['order'])
            for c_data in q_data['choices']:
                Choice.objects.create(
                    question=question,
                    text=c_data['text'],
                    is_correct=c_data['is_correct']
                )
        
        print(f"{len(questions_data)} yeni soru başarıyla veritabanına kaydedildi.")
        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                "type": "send.notification",
                "message": "Yapay zeka, istediğiniz konuda 10 yeni soru oluşturdu!",
                "status": "success"
            }
        )

    except Exception as e:
        error_message = f"Yapay zeka sorusu oluşturulurken bir hata oluştu: {e}"
        print(error_message)
        # HATA BİLDİRİMİ GÖNDER
        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                "type": "send.notification",
                "message": "Üzgünüz, sorular oluşturulamadı. Lütfen tekrar deneyin.",
                "status": "error"
            }
        )