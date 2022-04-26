import dataclasses
from tracemalloc import stop
import matplotlib.pyplot as plt
import os
import sqlite3
import unittest
import youtube_dl
from xml.sax import parseString
import googleapiclient.discovery
import csv

from bs4 import BeautifulSoup
import requests
import re
import json
#from rotten_tomatoes_client import RottenTomatoesClient

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
    """This function uses the youtube api in two ways:
    (1.) We use the api to search for the video id for each movie name's trailer
    (2.) We then use the api to get the movie trailer's statistics 
    The function returns a list with the movie's statistics [view count, like count, dislike count, favorite count, comment count"""

    API_KEY = 'AIzaSyC-2nikcshTBTeqZpjONjnfi5Fg9mz4E6I'
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
    """this function will take in a list of trailer stats and them in a csv file because we will need to collect this data 
    over 2-3 days since youtube limits the amount of data you can take per day"""

    with open('yt_trailer_data.csv', 'a') as f:
        writer = csv.writer(f)
        # make sure the data is a list of tuples of information from the youtube trailer api
        for tup in data:
            writer.writerow(tup)

    return None

def writing_movie_info(movie_lst, start_point, end_point):
    """This function will take in a list of movies and loop through each. The start point parameter is meant to help control how much data 
    is written at a time. Using this function, I can control what part of the movies we loop through."""
    
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
    

def write_movietrailer_table(csv_file, cur, conn):
    """This function will write the youtube statistics for each movie trailer in a database from a csv file and the rows of the 
    database will include movie id, trailer name, view count, like count, dislike count."""

    # create database with data from csv file

    cur.execute('DROP TABLE IF EXISTS Trailer_Stats')
    cur.execute('CREATE TABLE Trailer_Stats (title TEXT PRIMARY KEY, viewcount INTEGER, likecount INTEGER, dislikecount INTEGER)')

    # read csv file
    with open(csv_file, 'r') as f:
        file = csv.reader(f)
        n = 0
        for line in file:
            n+=1
            print(line)
            title = line[0]
            viewcount = line[1]
            likecount = line[2]
            dislikecount = line[3]
            cur.execute('INSERT OR IGNORE INTO Trailer_Stats (title,viewcount,likecount, dislikecount) VALUES (?,?,?, ?)', (title, viewcount, likecount, dislikecount))
    print(n)
    conn.commit()
            

    return None

def youtube_visualizations():
    "This function will work to visualize the data collected from youtube on the trailer. Specify specific visualizations here."
    pass

def tmdb_api():
    
    pass


def main():
    cur, conn = setUpDatabase('final_project_db.db')
    movie_tuples=get_top_movies()
    movies_table(movie_tuples, cur, conn)

    # gets list of movies titles
    movies = []
    for tup in movie_tuples: 
        movie = tup[0]
        movies.append(movie)

    # call functions to write trailer info for each trailer in csv file
    #writing_movie_info(movies, 0, 34)
    #writing_movie_info(movies, 34, 69)
    #writing_movie_info(movies, 69, 100) 
    lines = write_movietrailer_table('yt_trailer_data.csv', cur, conn)
    #top_titles = movies_table(movie_tuples, cur, conn)
    #get_rotten_score(top_titles)

main()
#class TestCases(unittest.TestCase):
    