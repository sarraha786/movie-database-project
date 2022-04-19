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


def get_top_movies():
    url = 'https://www.imdb.com/chart/top/?sort=us,desc&mode=simple&page=1'
    page = requests.get(url)
    if page.ok:
         soup = BeautifulSoup(page.content, 'html.parser')
         #print(soup.prettify())
         x=soup.find_all('td', class_='titleColumn')
         for i in x: 
             print(i.find('a').text)

#the year it was released, rating
      
            

#def get_youtube_info():



#This function is going to search each movie +trailer, get stats: likes, dislikes, views, comments






#Reddit, work on later


#visuulization
def main():
    get_top_movies()

main()
#class TestCases(unittest.TestCase):
    