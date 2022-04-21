import dataclasses
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


      
            

#def get_youtube_info():



#This function is going to search each movie +trailer, get stats: likes, dislikes, views, comments






#Reddit, work on later


#visuulization
def main():

    cur, conn = setUpDatabase('final_project_db.db')
    movie_tuples=get_top_movies()
    movies_table(movie_tuples, cur, conn)
main()
#class TestCases(unittest.TestCase):
    