from django.contrib import admin
from .models import Kana, QuizScore
from .models import Kanji 

# Register the custom Kana model.
# This makes it available in the Django admin interface.
@admin.register(Kana)
class KanaAdmin(admin.ModelAdmin):
    list_display = ('character', 'romaji', 'kana_type', 'audio_file')
    list_filter = ('kana_type',)
    search_fields = ('character', 'romaji')
    
# Register the QuizScore model to make it visible in the admin.
@admin.register(QuizScore)
class QuizScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz_type', 'score', 'date_taken')
    list_filter = ('quiz_type', 'date_taken')
    search_fields = ('user__username',)
admin.site.register(Kanji)