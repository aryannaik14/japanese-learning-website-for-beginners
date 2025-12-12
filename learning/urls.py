from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('login_signup/', views.login_signup_view, name='login_signup'),
    path('logout/', views.logout_view, name='logout'),
    
    # Flashcard pages
    path('hiragana/', views.hiragana_view, name='hiragana'),
    path('katakana/', views.katakana_view, name='katakana'),
    path('katakana/katakana.html', views.katakana_view, name='katakana'),
    path('kanji/', views.kanji_view, name='kanji'),
    path('katakana/kanji.html', views.kanji_view, name='kanji'),
    path('home/hiragana.html', views.hiragana_view, name='hiragana'),
    path('home/katakana.html', views.katakana_view, name='katakana'),
    path('home/kanji.html', views.kanji_view, name='kanji'),
    path('home/quiz.html', views.kanji_view, name='kanji'),
    
    # AI and Quiz functionality
    path('ai_helper/', views.ai_helper_view, name='ai_helper'),
    path('tts_view/', views.tts_view, name='tts_view'),
    path('katakana/quiz.html', views.quiz_view, name='quiz'),
    path('submit_quiz/', views.submit_quiz, name='submit_quiz'),
    path('kanji/grammar.html/', views.grammar_page, name='grammar'),
    path('grammar/', views.grammar_page, name='grammar'),
]
