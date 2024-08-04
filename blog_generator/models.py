from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class BlogPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    youtube_title = models.CharField(max_length=300)
    youtube_link = models.URLField()
    generated_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.youtube_title
    
class AIModel(models.Model):
    CATEGORIES = [
        ('Google', 'Google'),
        ('Meta', 'Meta'),
        ('Groq', 'Groq'),
        ('Mistral AI', 'Mistral AI'),
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.category} - {self.name}"

# # Add this method to easily populate the models
# def populate_models():
#     models = [
#         ('Google', 'gemma2-9b-it'),
#         ('Google', 'gemma-7b-it'),
#         ('Meta', 'llama-3.1-70b-versatile'),
#         ('Meta', 'llama-3.1-8b-instant'),
#         ('Meta', 'llama3-70b-8192'),
#         ('Meta', 'llama3-8b-8192'),
#         ('Meta', 'llama-guard-3-8b'),
#         ('Groq', 'llama3-groq-70b-8192-tool-use-preview'),
#         ('Groq', 'llama3-groq-8b-8192-tool-use-preview'),
#         ('Mistral AI', 'mixtral-8x7b-32768')
#     ]

#     for category, name in models:
#         AIModel.objects.create(category=category, name=name, is_default=(name == 'llama3-8b-8192'))