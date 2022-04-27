import dataclasses
import string
from tracemalloc import stop
import numpy as np
import matplotlib.pyplot as plt
import os
import sqlite3
import unittest
from xml.sax import parseString
import googleapiclient.discovery
import csv

from bs4 import BeautifulSoup
from tmdbv3api import TMDb
from tmdbv3api import Movie
import requests
import re
import json


# By Katie Lyngklip and Sarrah Ahmed
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn


def get_top_movies(file):
    with open(file, 'r') as f:
        html_file = f.read()
        soup = BeautifulSoup(html_file, 'html.parser')
        #print(soup.prettify())
         
        movies=[]
        movie_id=[]
        n = 1
        x=soup.find_all('td', class_='titleColumn')
        for i in x: 
            movie_id.append(n)
            movies.append(i.find('a').text)
            n += 1
         

        years=[]
        y=soup.find_all('span',class_='secondaryInfo')
        for i in y:
            year_no_parenth=i.text.replace("(","").replace(")","")
            years.append(int(year_no_parenth))

         
        rating_lst=[]
        ratings=soup.find_all('td',class_='ratingColumn imdbRating')
        for rating in ratings:
            rating_num=rating.text.strip()
            rating_lst.append(float(rating_num))

        final_tuple=(list(zip(movie_id,movies,years, rating_lst)))
        #print(final_tuple)
        #print('/n')
        return final_tuple

def movies_table(data,cur,conn):
   #create
   #cur.execute('DROP TABLE IF EXISTS Movies')
   cur.execute('CREATE TABLE IF NOT EXISTS Movies (Id PRIMARY KEY, Name TEXT, Year INTEGER, Rating NUMBER)')
 
   #find last one
   cur.execute('SELECT Id FROM Movies WHERE Id=(SELECT MAX(Id) From Movies)')
   start = cur.fetchone()
   if (start!=None):
       start = start[0] 
   else:
       start = 0

   for tup in data[start:start+25]:
       cur.execute('INSERT OR IGNORE INTO Movies (Id, Name,Year,Rating) VALUES (?,?,?,?)', (tup[0], tup[1],tup[2],tup[3]))
   conn.commit()
 
  
def movie_viz(cur):
   cur.execute('SELECT Year FROM Movies WHERE Year>2015')
   x=cur.fetchall()
   dic={}
   for year in x:
     if year[0] in dic:
         dic[year[0]]+=1
     else:
         dic[year[0]]=1
   my_labels=list(dic.keys())
   values=list(dic.values())
   colors=['yellow','green','orange','pink','blue','turquoise','red']
   # plt.pie(values, my_labels,autopct='%1.1f%%',shadow=True,startangle=90,colors=colors)
   plt.pie(values,labels = my_labels,autopct='%1.1f%%',colors=colors)
   plt.title('How many top movies are from the last five years',color='red')
   plt.axis('equal')
   plt.show()


# Youtube API---> using the API to get number of views, ratings, etc

def get_youtube_info(movie_name):
    API_KEY = 'AIzaSyDB0XXOOqGK6KMGqsUk0BqBL_Fg72Nx5Gw'
    youtube_api = googleapiclient.discovery.build("youtube", "v3", developerKey = API_KEY)
    trailer_name = str(movie_name) + ' Trailer'
    # api request 1 to get the trailer video info for each movie on the top 100 list
    request = youtube_api.search().list(
        part="id,snippet",
        type='video',
        q=trailer_name,
        maxResults=1)
    response = request.execute()
    video_id = response['items'][0]['id']['videoId']
    
    # api request 2 to get the video statistics (viewcount, likecount, favoritecount, commentcount)
    request = youtube_api.videos().list(
        part='snippet,contentDetails,statistics',
        id=video_id)
    response2 = request.execute()
    # trailer's statistics on youtube 
    viewcount = int(response2['items'][0]['statistics']['viewCount'])
    likecount = int(response2['items'][0]['statistics']['likeCount'])
    dislikecount = viewcount - likecount
    return [trailer_name, viewcount, likecount, dislikecount]

def writecsv_w_ytdata(data):
    with open('yt_trailer_data.csv', 'w') as f:
        writer = csv.writer(f)
        # make sure the data is a list of tuples of information from the youtube trailer api
        for tup in data:
            writer.writerow(tup)

    return None

def writing_movie_info(movie_lst, start_point, end_point):
    # get a list of movies you want to write their trailer data in the csv file
    data = []
    n = 0
    for movie in movie_lst: 
        if n >= start_point and n < end_point: 
            #trailer_stats = get_youtube_info(movie)
            data.append(movie)
            n += 1
        else:
            n += 1
            continue
    # get trailer data for each movie in specified list
    trailer_stats = []
    for title in data:
        trailer_stats.append(get_youtube_info(title))
    writecsv_w_ytdata(trailer_stats)

    return None


def requesting_yt_stats(movie_tuples):
    movies = []
    for tup in movie_tuples: 
        movie = tup[1]
        movies.append(movie) 

        #writing_movie_info(movies, 0, 34)
        #writing_movie_info(movies, 34, 69)
        #writing_movie_info(movies, 69, 100) 
    
    return None

def csv_reader(csv_file):
    """This function works to read the csvfile of youtube trailer data and turn it into a list of lists for each trailer."""
    data = []
    with open(csv_file, 'r') as f:
        file = csv.reader(f)
        n = -1
        for line in file:
            n+=1
            id = n
            title = line[0][:-8]
            viewcount = line[1]
            likecount = line[2]
            dislikecount = line[3]
            if title != '':
                data.append([id, title, viewcount, likecount, dislikecount])
    return data

def write_movietrailer_table(csv_data, cur, conn):
    """This function will write the youtube statistics for each movie trailer in a database from a csv file and the rows of the 
    database will include movie id, trailer name, view count, like count, dislike count."""

    cur.execute('CREATE TABLE IF NOT EXISTS Trailer_Stats (Id INTEGER PRIMARY KEY, title STRING, viewcount INTEGER, likecount INTEGER, dislikecount INTEGER)')
    cur.execute('SELECT Id FROM Trailer_Stats WHERE Id=(SELECT MAX(Id) From TMDB)')
    start = cur.fetchone()

    if (start!=None):
        start = start[0] 
    else:
        start = 0
    for trailer_info in csv_data[start:start + 25]:
        cur.execute('INSERT OR IGNORE INTO Trailer_Stats (Id,title,viewcount,likecount,dislikecount) VALUES (?,?,?,?,?)', (trailer_info[0], trailer_info[1], trailer_info[2], trailer_info[3], trailer_info[4]))
    conn.commit()

def youtube_calc(cur):
    """This function will select all the viewcounts, likecounts, and dislike counts. It will find the averages for each of these and
    write them in a csv_file to show our calculations"""

    cur.execute('SELECT viewcount, likecount, dislikecount FROM Trailer_Stats')
    viewcount_total = 0
    likes_total = 0
    dislikes_total = 0
    movie_total = 0
    for row in cur:
        movie_total += 1
        viewcount_total += row[0]
        likes_total += row[1]
        dislikes_total += row[2]
    
    with open('youtube_calculations.csv', 'w') as f:
        writer = csv.writer(f) 
        average_views = f"The average number of views for the movie trailers was {viewcount_total/movie_total}"
        average_likes = f"The average number of likes for the movie trailers was {likes_total/movie_total}"
        average_dislikes = f"The average number of dislikes for the movie trailers was {dislikes_total/movie_total}"
        for item in [average_views, average_likes, average_dislikes]:
            writer.writerow([item])

def youtube_viz(cur):
    # bar graph: spider man graph: views, likes, dislikes 
    cur.execute('SELECT title,viewcount,likecount,dislikecount FROM Trailer_Stats')
    data = {}
    for row in cur:
        if row[0] == 'Spider-Man: No Way Home':
            data['viewcount'] = row[1]
            data['likecount'] = row[2]
            data['dislikecount'] = row[3]
    count_types = list(data.keys())
    values = list(data.values())
    fig = plt.figure(figsize = (10,5))
    plt.bar(count_types, values, color='blue', width=0.5)
    plt.xlabel("Trailer Statistics")
    plt.ylabel("Count (in thousands)")
    plt.title("Spider Man Trailer Movie Statistics")
    plt.show()
        
def tmdb_api(movie_name):
    api = TMDb()
    api.api_key = '84800a5f39041de93dc3e66004914e00'
    movie = Movie()
    search = movie.search(movie_name)
    vote_average = search[0]['vote_average']
    release_date = search[0]['release_date'][:4]
    original_language = search[0]['original_language']
    vote_count = search[0]['vote_count']
    popularity = search[0]['popularity']
    return [movie_name, vote_average, release_date, original_language, vote_count, popularity]

def tmdb_database_prep(movie_tuples):
    id = 0
    output = []
    for tup in movie_tuples[:100]:
        id += 1
        movie_result = tmdb_api(tup[1])
        movie_result.append(id) 
        output.append(movie_result)
    return output

def tmdb_database(data, cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS TMDB (Id INTEGER PRIMARY KEY, movie_name STRING, vote_average INTEGER, release_date INTEGER, original_language STRING, vote_count INTEGER, popularity INTEGER)')
    cur.execute('SELECT Id FROM TMDB WHERE Id=(SELECT MAX(Id) From TMDB)')
    start = cur.fetchone()
    if (start!=None):
        start = start[0] 
    else:
        start = 0

    for lst in data[start:start+25]:
        cur.execute('INSERT OR IGNORE INTO TMDB (Id, movie_name, vote_average, release_date, original_language, vote_count, popularity) VALUES (?,?,?,?,?,?,?)', (lst[-1],lst[0],lst[1],lst[2],lst[3],lst[4],lst[5]))
    conn.commit()
    return None

def tmdb_calculation(cur):
    data = []
    cur.execute('SELECT Movies.Name, Movies.Rating, TMDB.vote_average FROM Movies JOIN TMDB ON Movies.Name = TMDB.movie_name GROUP BY Name')
    x=cur.fetchall()
    for movie in x:
        title = movie[0]
        movie_rating = movie[1]
        vote_average = movie[2]
        data.append([title,round(abs(movie_rating-vote_average),2)])
    with open('tmdb_calculations.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['Movie Name', 'Absolute Value Difference Between Ratings from IMDB and TMDB'])
        for item in data:
            writer.writerow(item)
    return None

def tmdb_viz(cur):
    data = {}
    cur.execute('SELECT movie_name, vote_average,vote_count,popularity FROM TMDB')
    for row in cur:
        if row[0] == 'Spider-Man: No Way Home':
            data['vote_count'] = row[2]
            data['popularity'] = row[3]
    keys = list(data.keys())
    values = list(data.values())
    fig = plt.figure(figsize = (10,5))
    plt.bar(keys, values, color='red', width=0.5)
    plt.xlabel("TMDB Statistics")
    plt.ylabel("Statistic Value")
    plt.title("Spider Man Movie TMDB Statistics")
    plt.show()

def main():
    cur, conn = setUpDatabase('final_project_db.db')
    movie_tuples=get_top_movies('Top 250 Movies - IMDb.html')
    movies_table(movie_tuples, cur, conn)
    #movie_viz(cur)
    
    # this function utilizes previously made functions to request movie trailer information for 100 of the movies in our movie list
    requesting_yt_stats(movie_tuples) 
    csv_data = csv_reader('yt_trailer_data.csv')
    youtube_db = write_movietrailer_table(csv_data, cur, conn)
    youtube_calc(cur)
    #youtube_viz(cur)

    tmdb_data = tmdb_database_prep(movie_tuples)
    tmdb_database(tmdb_data, cur, conn)
    tmdb_calculation(cur)
    #tmdb_viz(cur)

main()
#class TestCases(unittest.TestCase):
    