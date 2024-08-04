from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from .models import BlogPost, AIModel
import json
import os
import assemblyai as aai
from pytube import YouTube
import yt_dlp
from groq import Groq


# Create your views here.
@login_required
def index(request):
    return render(request, 'index.html')

def get_models(request):
    models = AIModel.objects.all()
    models_list = [{"id": model.id, "category": model.category, "name": model.name} for model in models]
    return JsonResponse(models_list, safe=False)

@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data['link']
            model_id = data.get('model_id')
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data sent'}, status=400)
            
        
        title = yt_title(yt_link)

        # Assembly AI
        transcription = get_transcription(yt_link)
        if not transcription:
            return JsonResponse({'error':'Failed to get transcription'}, status=500)
        
        # Groq Ai
        ai_model = AIModel.objects.get(id=model_id) if model_id else AIModel.objects.get(is_default=True)
        blog_content = generate_blog_from_transcription(transcription, ai_model.name)
        if not blog_content:
            return JsonResponse({'error':'Failed to geenerate blog'}, status=500)

        # Storing
        new_blog_article = BlogPost.objects.create(
            user = request.user,
            youtube_title = title,
            youtube_link = yt_link,
            generated_content = blog_content,
        )

        return JsonResponse({'content': blog_content})
    else:
        return JsonResponse({'error':'Invalid request method'}, status=405)

def yt_title(link):
    yt = YouTube(link)
    return yt.title

def download_audio(link):
    ffmpeg_location = r"C:\\ffmpeg\bin\\ffmpeg.exe"  # Adjust this path
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(settings.MEDIA_ROOT, '%(title)s.%(ext)s'),
        'ffmpeg_location': ffmpeg_location,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=True)
        filename = ydl.prepare_filename(info)
        return os.path.splitext(filename)[0] + '.mp3'

def get_transcription(link):
    audio_file = download_audio(link)
    aai.settings.api_key = os.environ.get("ASSEMBLY_AI_API_KEY")

    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)

    return transcript.text

def generate_blog_from_transcription(transcription, model_name):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
   
    prompt = f"Based on the following transcript from a YouTube video, write a comprehensive blog article. Write it based on the transcript, but don't make it look like a YouTube video; make it look like a proper blog article:\n\n{transcription}\n\nArticle:"
   
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model_name,
        max_tokens=1000
    )
   
    generated_content = chat_completion.choices[0].message.content.strip()
    return generated_content

def blog_list(request):
    blog_articles = BlogPost.objects.filter(user=request.user)
    return render(request, 'all-blogs.html', {'blog_articles': blog_articles})

def blog_details(request, pk):
    blog_article_detail = BlogPost.objects.get(id=pk)
    if request.user == blog_article_detail.user:
        return render(request, 'blog-details.html', {'blog_article_detail': blog_article_detail})
    else:
        return redirect('/')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        print(user, 'hehehhe')
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            error_message = "Invalid username or password"
            return render(request, 'login.html', {'error_message': error_message})
        
    return render(request, 'login.html')

def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repeatPassword = request.POST['repeatPassword']

        if password == repeatPassword:
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request, user)
                return redirect('/')
            except:
                error_message = 'Error creating account'
                return render(request, 'signup.html', {'error_message': error_message})
        else:
            error_message = 'Password do not match'
            return render(request, 'signup.html', {'error_message': error_message})
    else:
        return render(request, 'signup.html')

def user_logout(request):
    logout(request)
    return redirect('/')