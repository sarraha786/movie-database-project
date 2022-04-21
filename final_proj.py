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

   cur.execute('SELECT COUNT Movies.year ON Movies.year WHERE Movies.year>2015')
   x=cur.fetchall()
   print(x)
    # cur.execute('SELECT categories.category,COUNT(restaurants.category_id) FROM categories JOIN restaurants ON categories.id=restaurants.category_id GROUP BY category ')
    # x=cur.fetchall()
    
    # dic={}
    # for row in x:
    #     dic[row[0]]=row[1]
    # print(dic)

    # y_axis = list(dic.keys())
    # x_axis = list(dic.values())

#     Tasks = [300,500,700]

# my_labels = '2021','2020','2019','2018','2017','2016'

# plt.pie(Tasks,labels=my_labels,autopct='%1.1f%%')
# plt.title('My Tasks')
# plt.axis('equal')
# plt.show()
      
            

#def get_youtube_info():



#This function is going to search each movie +trailer, get stats: likes, dislikes, views, comments






#Reddit, work on later


#visuulization

#def write_csv(data, filename):







def main():

    cur, conn = setUpDatabase('final_project_db.db')
    movie_tuples=get_top_movies()
    movies_table(movie_tuples, cur, conn)
main()
#class TestCases(unittest.TestCase):
    