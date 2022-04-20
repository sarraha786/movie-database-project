import matplotlib.pyplot as plt
import os
import sqlite3
import unittest
from xml.sax import parseString

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
         imdb_dict={}
         movies=[]
         x=soup.find_all('td', class_='titleColumn')
         for i in x: 
             movies.append(i.find('a').text)
         

         years=[]
         y=soup.find_all('span',class_='secondaryInfo')
         for i in y:
             
             years.append(int(i).text.replace("(","").replace(")",""))
        
         rating_lst=[]
         ratings=soup.find_all('td',class_='ratingColumn imdbRating')
         for rating in ratings:
             
             rating_lst.append(float(rating).text.strip())
         
         for movie in movies:
             for year in years:
                 for rating in rating_lst:
                     imdb_dict[movie]=year,rating
         print(imdb_dict)
#         cur.execute("DROP TABLE IF EXISTS Movies")
    #      cur.execute("CREATE TABLE Movies ('title' TEXT PRIMARY KEY, 'year' INTEGER, 'rating' NUMBER)")
    #      for i in range(len(species)):
    #          cur.execute("INSERT INTO Species (id,title) VALUES (?,?)",(i,species[i]))
    # conn.commit()

#the year it was released, rating
      
            

#def get_youtube_info():



#This function is going to search each movie +trailer, get stats: likes, dislikes, views, comments






#Reddit, work on later


#visuulization
def main():
    get_top_movies()
    setUpDatabase('final_project_db')
main()
#class TestCases(unittest.TestCase):
    