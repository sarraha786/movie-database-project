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


#this function is getting the official building name, address, and building category for each building on campus.
#  It will output a list of dictionaries that looks like this: [{'Mason Hall': 	('419 STATE ST Ann Arbor, MI 48109', 'academic')}]
def get_umich_buildings():
    url = 'https://maps.studentlife.umich.edu'
    page = requests.get(url)
    if page.ok:
        soup = BeautifulSoup(page.content, 'html.parser')
        tags = soup.find_all('div', class_='ui list link-block')
        for tag in tags:
            return tag
        
        




#API ONE endpoint will be 'address', search_text will be the string of the address itself
def get_coordinates(search_text):
    # create request
    url = f"https://api.mapbox.com/geocoding/v5/address/{search_text}.json"
    umich_dict = get_umich_buildings()
    coordinate_dict = {}
    r=requests.get(url)
    contents=json.loads(r.text)


    pass
    






def main():

    print(get_umich_buildings())
    #for building in umich_dict.keys():
        #address = umich_dict[building][0]
        #get_coordinates(address)

main()
#class TestCases(unittest.TestCase):
    #def test_get_umich_buildings(self):