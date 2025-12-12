# A note on security:
# For production, it's best practice to store your API key in an environment variable,
# not directly in your views.py file. You can access it like this:
# import os
# GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from .models import Kana, Kanji, QuizScore
import json
import requests
import random
import os

def login_signup_view(request):
    if request.method == "POST":
        if 'login' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
                return redirect('login_signup')

        elif 'signup' in request.POST:
            username = request.POST.get('signup_username')
            email = request.POST.get('email')
            password = request.POST.get('signup_password')
            
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already taken. Please choose another.")
                return redirect('login_signup')
            elif User.objects.filter(email=email).exists():
                messages.error(request, "An account with this email already exists.")
                return redirect('login_signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                login(request, user)
                return redirect('home')

    return render(request, 'learning/login_signup.html')

def home(request):
    return render(request, 'learning/home.html')

def flashcards(request):
    """
    Renders the generic flashcards page.
    """
    kana_type = request.GET.get('type', 'Hiragana')
    kana_list = Kana.objects.filter(kana_type=kana_type).order_by('character')
    return render(request, 'learning/flashcards.html', {'kana_list': kana_list, 'kana_type': kana_type})

def logout_view(request):
    logout(request)
    return redirect('home')

def ai_helper_view(request):
    # Get your API key from a secure location.
    api_key = ''

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_prompt = data.get('prompt', '')

            if not user_prompt:
                return JsonResponse({'error': 'No prompt provided'}, status=400)

            prompt = f"As a Japanese learning assistant, provide a concise and clear response to this request: {user_prompt}"
            
            payload = { "contents": [{ "parts": [{"text": prompt}] }] }
            
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={api_key}"

            response = requests.post(api_url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
            response.raise_for_status()

            result = response.json()
            if result.get('candidates') and result['candidates'][0]['content']['parts'][0]['text']:
                ai_response = result['candidates'][0]['content']['parts'][0]['text']
                return JsonResponse({'response': ai_response})
            else:
                return JsonResponse({'error': 'API did not return a valid response'}, status=500)

        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': f'API request failed: {str(e)}'}, status=500)
        except Exception as e:
            return JsonResponse({'error': f'An internal server error occurred: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def tts_view(request):
    # Get your API key from a secure location.
    api_key = ''

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text_to_speak = data.get('text', '')

            if not text_to_speak:
                return JsonResponse({'error': 'No text provided'}, status=400)

            # Define the prompt for the TTS model
            prompt = f"Say this in a cheerful Japanese voice: {text_to_speak}"

            payload = {
                "contents": [{ "parts": [{ "text": prompt }] }],
                "generationConfig": {
                    "responseModalities": ["AUDIO"],
                    "speechConfig": {
                        "voiceConfig": { "prebuiltVoiceConfig": { "voiceName": "Puck" } }
                    }
                },
                "model": "gemini-2.5-flash-preview-tts"
            }
            
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={api_key}"

            response = requests.post(api_url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
            response.raise_for_status()

            result = response.json()
            part = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0]
            audio_data = part.get('inlineData', {}).get('data')
            mime_type = part.get('inlineData', {}).get('mimeType')

            if audio_data and mime_type:
                return JsonResponse({'audio_data': audio_data, 'mime_type': mime_type})
            else:
                return JsonResponse({'error': 'TTS generation failed'}, status=500)

        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': f'TTS API request failed: {str(e)}'}, status=500)
        except Exception as e:
            return JsonResponse({'error': f'An internal server error occurred: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
def hiragana_view(request):
    """
    Renders the hiragana flashcard page with all hiragana characters from the database.
    """
    kana_list = Kana.objects.filter(kana_type='Hiragana').order_by('character')
    return render(request, 'learning/hiragana.html', {'kana_list': kana_list})
def katakana_view(request):
    """
    Renders the katakana flashcard page.
    """
    kana_list = Kana.objects.filter(kana_type='Katakana').order_by('character')
    return render(request, 'learning/katakana.html', {'kana_list': kana_list})
def kanji_view(request):
    """
    Renders the kanji page if the user is authenticated and has passed the quiz.
    """
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to view the Kanji section.")
        return redirect('login_signup')
    
    # Check if the user has a recent quiz score of 10 or more.
    try:
        min_score = 10
        last_score = QuizScore.objects.filter(user=request.user, quiz_type='Combined')\
                                     .order_by('-date_taken').first()
        if not last_score or last_score.score < min_score:
            messages.error(request, f"Please pass the test first (score {min_score}/15 min).")
            return redirect('quiz')
            
    except QuizScore.DoesNotExist:
        messages.error(request, f"Please pass the test first (score {min_score}/15 min).")
        return redirect('quiz')

    # Fetch all Kanji from the database
    kanji_list = Kanji.objects.all().order_by('kanji')
    # Pass the list to the template
    return render(request, 'learning/kanji.html', {'kanji_list': kanji_list})

def quiz_view(request):
    """
    Renders a quiz page with 15 random Hiragana and Katakana questions.
    """
    hiragana_chars = list(Kana.objects.filter(kana_type='Hiragana'))
    katakana_chars = list(Kana.objects.filter(kana_type='Katakana'))
    
    all_chars = hiragana_chars + katakana_chars
    
    if len(all_chars) < 15:
        messages.error(request, "Not enough characters in the database to create a quiz. Please add more.")
        return redirect('home')
        
    random_questions = random.sample(all_chars, 15)
    
    for question in random_questions:
        correct_answer = question.romaji
        
        # Get all other unique romaji values to use as incorrect options
        all_romaji = list(Kana.objects.exclude(pk=question.pk).values_list('romaji', flat=True).distinct())
        
        # Select 3 random incorrect answers
        incorrect_options = random.sample(all_romaji, 3)
        
        options = [correct_answer] + incorrect_options
        random.shuffle(options)
        
        question.options = options
        
    context = {
        'questions': random_questions,
    }
    return render(request, 'learning/quiz.html', context)


def submit_quiz(request):
    """
    Handles the quiz submission, scores the answers, and saves the result.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            answers = data.get('answers', {})
            
            score = 0
            questions = Kana.objects.filter(pk__in=answers.keys())
            
            for question in questions:
                user_answer = answers.get(str(question.pk))
                if user_answer and user_answer == question.romaji:
                    score += 1

            if request.user.is_authenticated:
                QuizScore.objects.create(
                    user=request.user,
                    quiz_type='Combined',
                    score=score
                )
            
            min_score = 10
            is_passed = score >= min_score
            
            response_data = {
                'score': score,
                'total': 15,
                'is_passed': is_passed,
                'redirect_url': reverse('kanji') if is_passed else None,
            }
            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)
def grammar_page(request):

    return render(request, 'learning/grammar.html')
