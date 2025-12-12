from django.db import models
from django.contrib.auth.models import User

class Kana(models.Model):
    """
    Model to store Japanese characters (Kana and Kanji) for flashcards.
    """
    # The actual Japanese character (e.g., 'あ' or '日')
    character = models.CharField(max_length=10, unique=True, help_text="The Japanese character.")
    
    # The Romanized representation of the character (e.g., 'a' or 'nichi')
    romaji = models.CharField(max_length=20, help_text="The Romanization of the character.")
    
    # The type of character (e.g., 'Hiragana', 'Katakana', 'Kanji')
    kana_type = models.CharField(max_length=20, choices=[
        ('Hiragana', 'Hiragana'),
        ('Katakana', 'Katakana'),
        ('Kanji', 'Kanji'),
    ], help_text="The type of the character.")
    
    # An optional audio file for pronunciation
    audio_file = models.FileField(upload_to='audio/', blank=True, null=True, help_text="Audio pronunciation file.")

    def __str__(self):
        """String representation of the model."""
        return f"{self.character} ({self.romaji})"

    class Meta:
        verbose_name = "Kana Character"
        verbose_name_plural = "Kana Characters"
        ordering = ['kana_type', 'romaji']

class QuizScore(models.Model):
    """
    Model to store a user's quiz scores.
    """
    # The user who took the quiz
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # The type of quiz (e.g., 'Hiragana', 'Katakana')
    quiz_type = models.CharField(max_length=20, choices=[
        ('Hiragana', 'Hiragana'),
        ('Katakana', 'Katakana'),
        ('Kanji', 'Kanji'),
    ])
    
    # The score received in the quiz
    score = models.IntegerField(help_text="The score for the quiz (e.g., number of correct answers).")
    
    # The date the quiz was taken
    date_taken = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s {self.quiz_type} Quiz Score: {self.score}"

    class Meta:
        ordering = ['-date_taken']
class Kanji(models.Model):
    kanji = models.CharField(max_length=1)
    meaning = models.TextField()
    onyomi = models.CharField(max_length=50)
    kunyomi = models.CharField(max_length=50)
    onyomi_example = models.CharField(max_length=100)
    onyomi_example_reading = models.CharField(max_length=100)
    kunyomi_example = models.CharField(max_length=100)
    kunyomi_example_reading = models.CharField(max_length=100)
    stroke_order_svg = models.TextField()

    def __str__(self):
        return self.kanji