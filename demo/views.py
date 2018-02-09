# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, logout, login

import datetime
import random
import logging
import time
from django.db import connection


logger = logging.getLogger(__name__)
# Create your views here.
def index(request):
	return render(request, "index.html")

def getRandomWordOld(request):
	l = ["Joey","John","Mike"]
	return HttpResponse(random.choice(l))

def getRandomWordold(request):
	movie_instance = Movies.objects.order_by('?').first()
	movie_instance_id1 = Movies.objects.filter(movieid=1).order_by('?').first()
	return HttpResponse(movie_instance_id1.title)
def getRandomWord(request):
	with connection.cursor() as cursor:
		cursor.execute("SELECT title FROM movies ORDER BY Rand()")
		row = cursor.fetchone()
		return HttpResponse(row)

def signup(request):
    return render(request, "signup.html")

def login(request):
    return render(request, "login.html")

def chat(request):
    return render(request, "chat.html")

def Post(request):
    userid = request.session.get('userId')
    if request.method == "POST":
        msg = request.POST.get('msgbox','')
        with connection.cursor() as cursor:
	    cursor.execute("INSERT INTO demo_chat VALUES ( %s,NULL,%s)",[userid,msg])
        return JsonResponse({'msg':msg})
    else:
        return HttpResponse('Request must be POST.')

def Messages(request):
    c = "All messages"
    return render(request, 'messages.html', {'chat': c})


def Temp(request):
    next = request.GET.get('next', '/chat/')
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(next)
            else:
                return HttpResponse("Account is not active at the moment.")
        else:
            return HttpResponseRedirect(settings.LOGIN_URL)
    return render(request, "temp.html", {'next': next})
	


def authenticate(request):
  
    with connection.cursor() as cursor:
        cursor.execute("SELECT userId,fullname FROM users WHERE username=%s and password=%s",[request.POST.get('username',''), request.POST.get('password','')])
        data = cursor.fetchone()

	if data is None:
            return render(request, "login.html",{"sentence":"Incorrect password"})
	request.session['userId'] = float(data[0])
	return render(request, "index.html", {"fullname":data[1]})
    

def getMovie(request):
	movieid = request.POST.get('movieID', '')
	with connection.cursor() as cursor:
		cursor.execute("SELECT title,genres FROM movies WHERE movieId=%s GROUP BY movieId", [movieid])
		data = cursor.fetchone()
		cursor.execute("SELECT tag FROM tags WHERE movieId=%s GROUP BY movieId", [movieid])
		tags = cursor.fetchone()
		cursor.execute("SELECT avg(rating) FROM ratings WHERE movieId=%s GROUP BY movieId", [movieid])
		r = cursor.fetchone()
	if data is None or r is None:
		return render(request, "index.html", {"sentence":"Invalid movie id"})
	ratings = float(r[0])
	if tags is None:
		tags = [""]
	return render(request, "index.html", {"title":data[0],"genres":data[1],"tags":tags[0],"ratings":ratings})
       

def insertMovieRating(request):
	userid = request.session.get('userId','')
	movieid = request.POST.get('insertMovieid','')
	rating = request.POST.get('insertRating','')
	if(userid=='userid' or userid=='' or movieid=='movieid' or movieid=='' or rating=='' or rating=='rating'):
		return render(request,"index.html",{"sentece":"Please fill in all the three fields"})
	ts = time.time()
	with connection.cursor() as cursor:
		cursor.execute("SELECT userId FROM ratings WHERE userId=%s and movieId=%s",[userid,movieid])
		userId = cursor.fetchone()
		if(userId is not None):
			return render(request,"index.html",{"sentence":"You have already rated this movie, please use update instead of insert."})
		cursor.execute("INSERT INTO ratings VALUES(%s,%s,%s,%s)",[userid,movieid,rating,ts])
	return render(request,"index.html",{"sentence":"Successfully insert your rating of this movie"})

def deleteMovieRating(request):
	movieid = request.POST.get('deleteMovieid','')
	userid = request.session.get('userId')
	if(userid=='' or userid=='userid' or movieid=='' or movieid=='movieid'):
		return render(request,"index.html",{"sentence":"Please enter both userID and movieID"})
	with connection.cursor() as cursor:
		cursor.execute("SELECT rating FROM ratings WHERE movieId=%s and userId=%s", [movieid,userid])
                rating = cursor.fetchone()
        	if rating is not None:
        		cursor.execute("DELETE FROM ratings WHERE movieId=%s and userId=%s", [movieid,userid])
        		return render(request,"index.html",{"sentence":"Delete successfully"})
	return render(request,"index.html",{"sentence":"User rating or Movie does not exist"})

def updateMovieRating(request):
        userid = request.session.get('userId')
        movieid = request.POST.get('updateMovieid','')
        rating = request.POST.get('updateRating','')
        if(userid=='userid' or userid=='' or movieid=='movieid' or movieid=='' or rating=='rating' or rating==''):
             return render(request,"index.html",{"sentence":"Please fill in all the three fields"})
        ts = time.time()
        with connection.cursor() as cursor:
                cursor.execute("SELECT userId,movieId FROM ratings WHERE movieId=%s and userId=%s",[movieid,userid])
                data = cursor.fetchone()
                if data is not None:
                     cursor.execute("UPDATE ratings SET rating=%s WHERE movieId=%s and userId=%s", [rating, movieid, userid])
                     return render(request,"index.html",{"sentence":"Update successfully"})
                cursor.execute("INSERT INTO ratings VALUES(%s,%s,%s,%s)",[userid,movieid,rating,ts])
                return render(request,"index.html",{"sentence":"Successfully update your rating of this movie"})


def create_user(request):
    fullname = request.POST.get('fullname','')
    username = request.POST.get('username','')
    password = request.POST.get('password','')
    if fullname=='' or username=='' or password=='':
	return render(request, "signup.html",{"sentence":"Invalid"})
    with connection.cursor() as cursor:
        cursor.execute("SELECT userId FROM users WHERE username=%s",[username])
        userId = cursor.fetchone()
        if userId is not None:
	    return render(request, "signup.html",{"sentence":"username already exists"})

        cursor.execute("INSERT INTO users VALUES(NULL, %s, %s, %s)",[fullname, password, username])
        cursor.execute("SELECT userId FROM users WHERE username=%s and password=%s",[request.POST.get('username',''), request.POST.get('password','')])
        userId = cursor.fetchone()
	
        if userId is None:
            return render(request, "login.html",{"sentence":"Incorrect password"})
        return render(request, "index.html",{"userId":float(userId[0])})

def recommend(request):
    userid = request.session.get('userId','')
    weight = {}
    score = {}
    with connection.cursor() as cursor:
        cursor.execute("SELECT rating,genres  FROM ratings,movies WHERE ratings.movieId=movies.movieId and userId=%s", [userid])
        while True:
	    row = cursor.fetchone()
	    if row == None:
	        break
	    genres = row[1].split("|")
	    rating = float(row[0])
	    for g in genres:
	        if weight.has_key(g):
		    weight[g] += rating
		else:
		    weight[g] = rating

	cursor.execute("SELECT movieId,genres FROM movies",[])
	while True:
	    row = cursor.fetchone()
	    if row == None:
		break
	    genres = row[1].split("|")
	    mid = row[0]
	    score[mid] = 0
	    for g in genres:
		if weight.has_key(g):
		    score[mid]+=weight[g]
		else:
		    score[mid]-=0.1

	result = sorted(score.iteritems(), key=lambda (k,v):(v,k), reverse = True)[:5]
	rec_list="We recommend: \n"
	l = ', '.join('%s' for mid,v in result)
	cursor.execute("DROP VIEW IF EXISTS movie_ratings",[])
	cursor.execute("CREATE VIEW movie_ratings as SELECT movies.movieId,title,AVG(rating) as avg_rating FROM movies,ratings WHERE movies.movieId in (%s) and movies.movieId=ratings.movieId GROUP BY movies.movieId ORDER BY AVG(rating) desc" %l, tuple([str(mid) for mid, v in result]))
	cursor.execute("SELECT movieId,title,avg_rating FROM movie_ratings",[])
	while True:
	    row = cursor.fetchone()
	    if row==None:
		break
	    rec_list+=str(row[1].decode('utf-8'))+ " rating:"+str(float(row[2]))+ " matching score: "+ str(float(score[row[0]]))+"\n"
	return render(request, "index.html",{"recommendation":rec_list})
	    

def predict(request):
    userid = request.session.get('userId','')
    genres = request.POST.get('tags','')
    gs = (genres).split(",")
    s_rate = 0.0
    s_total = 0.0
    b_rate = 0.0
    b_total = 0.0
    with connection.cursor() as cursor:
        cursor.execute("SELECT rating,genres  FROM ratings,movies WHERE ratings.movieId=movies.movieId", [])
        while True:
            row = cursor.fetchone()
            if row==None:
                break
            res_genres = row[1].split('|')
            if(gs[0] in res_genres and gs[1] in res_genres):
	        b_rate+=float(row[0])
	        b_total+=1
            elif(gs[0] in res_genres or gs[1] in res_genres):
	        s_rate+=float(row[0])
 	        s_total+=1
    if b_total==0 or s_total==0:
	return render(request, "index.html",{"predict":"Invalid key words"})
    result = 0.8*(b_rate/b_total)+0.2*(s_rate/s_total)
    return render(request, "index.html",{"predict":"Predict rating: "+str(result)})
