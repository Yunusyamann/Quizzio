from django.shortcuts import render
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt # <-- BU IMPORT SATIRI ÇOK ÖNEMLİ
import json
from .models import GameSession, Player
from .tasks import generate_questions_from_prompt
# Bu, Vue uygulamasını sunan ana view olacak
def index(request, *args, **kwargs):
    return render(request, 'index.html')

@csrf_exempt # <-- BU DECORATOR SATIRI ÇOK ÖNEMLİ
def api_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'success': True, 'username': user.username})
            else:
                return JsonResponse({'success': False, 'error': 'Kullanıcı adı veya şifre hatalı.'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Geçersiz istek metodu'}, status=405)

def create_game_session(request):
    # Bu view'ın çalışması için kullanıcının giriş yapmış olması gerekir
    if not request.user.is_authenticated or request.user.username != 'yunus':
        return HttpResponseForbidden("Yetkiniz yok.")
    
    session = GameSession.objects.create(host=request.user)
    return JsonResponse({'success': True, 'session_code': session.session_code})

@csrf_exempt
def api_generate_questions(request):
    if not request.user.is_authenticated or request.user.username != 'yunus':
        return HttpResponseForbidden("Yetkiniz yok.")
    
    if request.method == 'POST':
        data = json.loads(request.body)
        prompt = data.get('prompt')
        if not prompt:
            return JsonResponse({'success': False, 'error': 'Prompt boş olamaz.'}, status=400)
        
        # Asıl işi Celery'ye devrediyoruz
        generate_questions_from_prompt.delay(prompt, request.user.id)

        return JsonResponse({'success': True, 'message': 'Sorular arka planda oluşturulmaya başlandı. Hazır olduğunda bir bildirim alacaksınız.'})
    
    return JsonResponse({'error': 'Geçersiz istek metodu'}, status=405)