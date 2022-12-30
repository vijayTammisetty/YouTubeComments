from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from sentimentapp.models import UserModel

#  API data libraries
import requests
from django.conf import settings
from isodate import parse_duration
import os
from googleapiclient.discovery import build
import pandas as pd

import re

from bs4 import BeautifulSoup
# from textblob import TextBlob
from googletrans import Translator
import nltk 
from nltk.sentiment import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')

# Create your views here.

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        print(email,password)

        try:
            user = UserModel.objects.get(email=email, password=password)
            
            if user.status == 'Accept':
                request.session['user_id'] = user.user_id
                print(user.user_id,'hi user')
                messages.success(request,'user login successsfully')
                return redirect('user-home')
            else:
                messages.info(request, 'your account is not approved at !!')
                return redirect('user_login')
        except :
            messages.info(request,'Wrong email and password')
            return redirect('user_login')
    return render(request, 'user/user_login.html')

def user_register(request):
    if request.method == 'POST' and  'profile' in request.FILES:
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('pass1')
        # con_pass = request.POST.get('pass2')
        profile = request.FILES['profile']
        phone = request.POST.get('num')
        country = request.POST.get('country')

        try:
            UserModel.objects.get(email = email)
            messages.warning(request, ' Email alresdy exists')
            return redirect('register')

        except:
            UserModel.objects.create(
                name = name,
                email = email,
                password = password,
                # con_password = con_pass,
                profile = profile,
                phone = phone,
                country = country
            )
            messages.success(request, 'User Registered successfully ')
            return redirect('user_login')

    return render(request, 'user/register.html')


def home(request):
    return render(request, 'user/index.html')

def profile(request):
    user_id = request.session['user_id']
    print(user_id)
    user  = UserModel.objects.get(pk=user_id)
  
    if request.method == 'POST':
        user_name = request.POST.get('name')
        user_email = request.POST.get('email')
        user_number = request.POST.get('num')
        user_country = request.POST.get('country')

        if not request.FILES.get('profile',False):
            user.name = user_name
            user.email = user_email
            user.phone = user_number
            user.country = user_country

        if request.FILES.get('profile',False):
            image = request.FILES['profile']
            user.name = user_name
            user.email = user_email
            user.phone = user_number
            user.country = user_country
            user.profile = image
        user.save()
        return redirect('profile')

    return render(request,'user/user-profile.html', {'user':user})


# ========== youtube Api for extracting youtube videos and its comments =======================

def api_search(request):
   
    ''' getting all the data from the youtube using api'''

    if request.method == 'POST':
        youtybe_search_url = ' https://www.googleapis.com/youtube/v3/search'
        youtube_video_url = 'https://www.googleapis.com/youtube/v3/videos'
        # comments_thread_url =' https://www.googleapis.com/youtube/v3/commentThreads' 
        s = request.POST['search']
        search_params = {
            'part': 'snippet',
            'q' : s,
            'key' : settings.YOUTUBE_API_KEY,
            'maxResults':1,
            'type': 'comments'
        }
    
        req = requests.get(youtybe_search_url, params=search_params) 
        # print(req.text)
        # print('video-id :',req.json()['items'][0]['id']['videoId'])
        try:
            results = req.json()['items']

        except:
            print('except')
            messages.error(request,'Enter valid api key Items not found')
            return redirect('api_search')
        # print(results)
       
        # print("Add new api Key")


        ''' video id's extracting to get the video's from the youtube '''

        videos_ids = []
        for results in results:
            videos_ids.append(results['id']['videoId'])
        
#============================ videos section ==============================

        ''' extracting the video's from the youtube using video-id's which we have extracted above'''    

        video_params = {
            'key' : settings.YOUTUBE_API_KEY,
            'part': 'snippet,contentDetails',
            'id': ','.join(videos_ids)
        }

        video_re = requests.get(youtube_video_url, params=video_params)
        res = video_re.json()['items']
        # print(res)
        videos = []
        for i in res:
            #     url.replace('https://www.youtube.com/watch?v=',"https://youtube.com/embed/")
            video_data = {
                'title':i['snippet']['title'],
                'id': i['id'],
                'url':f'https://youtube.com/embed/{i["id"]}', 
                'duration':int(parse_duration(i['contentDetails']['duration']).total_seconds()/ 60 ),
                'thumbnails':i['snippet']['thumbnails']['high']['url']
            }
            videos.append(video_data)

#=============================== comments section ============================== 

        ''' Extracting the comments using video-id's based on perticular video '''

        comments = []
        
        for id in videos_ids: 
            ver = 'v3'
            youtube = build( 'youtube',ver, developerKey=settings.YOUTUBE_API_KEY)

            res = youtube.commentThreads().list(
                part = 'id,snippet,replies',
                # order = 'relevence',
                videoId =id,
                maxResults = 50,
            )
            responce = res.execute()

            resl = responce['items']
            
            for com in resl:
                com_ts = {
                    'image':com['snippet']['topLevelComment']['snippet']['authorProfileImageUrl'],
                    'name':com['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                    'comment':com['snippet']['topLevelComment']['snippet']['textDisplay']
                }
                
                come = BeautifulSoup(com_ts['comment'])
                a = come.get_text()
                # print(a,'plain commentsss')
                # comments.append(com_ts)

                ''' Translating the comments from all languages in to English '''
                if a:
                    try:
                        translator = Translator()
                        trans = translator.detect(a)
                    
                        if trans.lang != "en":
                            out = translator.translate(a,dest="en")
                            comment = out.text
                            com_ts['comment'] = comment
                           
                        else:
                            com_ts['comment'] = a
                            # comments.append(com_ts)

                    
                    except:
                        comment = a 
                        b = ''.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\s+)"," ",comment).split())
                        print(b)
                        com_ts['comment'] = b
                        
 # =============================  sentiment analysis on youtube video comments  ==================================

                    # analysis = TextBlob(str(com_ts['comment']))
                    sen = SentimentIntensityAnalyzer() 
                    analysis = sen.polarity_scores(com_ts['comment'])
                        
                    sentiments = ''
                    
                    # print(analysis['compound'])
                    if analysis['compound'] >= 0.5:
                        sentiments = 'Very Positive'
                    elif analysis['compound'] > 0 and analysis['compound'] < 0.5:
                        sentiments = 'Positive'
                    elif analysis['compound'] < 0 and analysis['compound'] >= -0.5:
                        sentiments = 'Negative'
                    elif analysis['compound'] <= -0.5:
                        sentiments = 'Very Negative'
                    else:
                        sentiments = 'Neutral'
                    com_ts['sentiment'] = sentiments
                    comments.append(com_ts) 

 
#   ================ overall sentiment analysis in  % =========================

        pos = [sentiment for sentiment in comments if sentiment['sentiment']=='Positive']
        verypos = [sentiment for sentiment in comments if sentiment['sentiment']=='Very Positive']
        nege = [sentiment for sentiment in comments if sentiment['sentiment']=='Negative']
        verynege = [sentiment for sentiment in comments if sentiment['sentiment']=='Very Negative']
       
        neutral = len(comments) - (len(nege) + len(pos) + len(verypos) + len(verynege))
        try:
            positive = float(format(100 * len(pos) / len(comments))) 
            verypositive = float(format(100 * len(verypos) / len(comments)))
            negetive = float(format(100 * len(nege) / len(comments)))
            verynegetive = float(format(100 * len(verynege) / len(comments)))
            nutraltotal = float(format(100 * neutral / len(comments)))

        except:
            print('Comments not found :Refresh your browser')
            messages.info(request,'Invalid input Enter again')
            return redirect('api_search')


        context = {
            'videos':videos,
            'comments':comments,
            'positive':positive,
            'verypositive':verypositive,
            'negetive':negetive,
            'verynegetive':verynegetive,
            'neutral':nutraltotal,

            }
        return render(request, 'user/api-search.html', context)
    return render(request, 'user/api-search.html')

def logout(request):
    messages.success(request,'User logout successfully')
    return redirect('home')


