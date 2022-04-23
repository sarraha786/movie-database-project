import dataclasses
import matplotlib.pyplot as plt
import os
import sqlite3
import unittest
import youtube_dl
from xml.sax import parseString
import googleapiclient.discovery

from bs4 import BeautifulSoup
import requests
import re
import json

# By Katie Lyngklip and Sarrah Ahmed
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn


def get_top_movies():
    url = 'https://www.imdb.com/chart/top/?sort=us,desc&mode=simple&page=1'
    page = requests.get(url)
    if page.ok:
         soup = BeautifulSoup(page.content, 'html.parser')
         #print(soup.prettify())
         
         movies=[]
         x=soup.find_all('td', class_='titleColumn')
         for i in x: 
             movies.append(i.find('a').text)
         

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

         final_tuple=(list(zip(movies,years, rating_lst)))
        
         return final_tuple
        
def movies_table(data,cur,conn):
   print(data[0])
   cur.execute('DROP TABLE IF EXISTS Movies')
   cur.execute('CREATE TABLE Movies (Name TEXT PRIMARY KEY, Year INTEGER, Rating NUMBER)')
   for tup in data:
       cur.execute('INSERT OR IGNORE INTO Movies (Name,Year,Rating) VALUES (?,?,?)', (tup[0], tup[1],tup[2]))
   conn.commit()
   
#    for tup in data: 
#        name = tup[0]
#        year=tup[1]
#        rating=tup[2]
#    for i in range(len(data)):
#        cur.execute('INSERT OR IGNORE INTO Movies (Name,Year,Rating) VALUES (?,?,?)', (name, year,rating))
#    conn.commit()

# test 


      
            
# Youtube API---> using the API to get number of views, ratings, etc

def get_youtube_info(movie_name):
    API_KEY = 'AIzaSyAD2NINir17W0mXfiWF91_BdI-XYvbZwKc'
    youtube_api = googleapiclient.discovery.build("youtube", "v3", developerKey = API_KEY)
    trailer_name = movie_name + ' Trailer'
    # api request 1 to get the trailer video info for each movie on the top 250 list
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
    viewcount = response2['items'][0]['statistics']['viewCount']
    likecount = response2['items'][0]['statistics']['likeCount']
    favoritecount = response2['items'][0]['statistics']['favoriteCount']
    commentcount = response2['items'][0]['statistics']['commentCount']
    return (viewcount, likecount, favoritecount, commentcount)
    

#This function is going to search each movie +trailer, get stats: likes, dislikes, views, comments






#Reddit, work on later


#visuulization
def main():

    cur, conn = setUpDatabase('final_project_db.db')
    movie_tuples=get_top_movies()
    movies_table(movie_tuples, cur, conn)
    get_youtube_info()
main()
#class TestCases(unittest.TestCase):
    