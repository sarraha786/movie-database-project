import matplotlib.pyplot as plt
import os
import sqlite3
import unittest

#worked with Katie Lyngklip

def get_restaurant_data(db_filename):
    """
    This function accepts the file name of a database as a parameter and returns a list of
    dictionaries. The key:value pairs should be the name, category, building, and rating
    of each restaurant in the database.
    """
    source_dir = os.path.dirname(__file__)
    full_path = os.path.join(source_dir, db_filename)

    conn = sqlite3.connect(full_path)
    cur = conn.cursor()
    cur.execute('SELECT restaurants.name,categories.category, buildings.building, restaurants.rating FROM restaurants JOIN categories ON categories.id=restaurants.category_id JOIN buildings ON buildings.id=restaurants.building_id')
    x=cur.fetchall()
    output = []
    for row in x:
       dic = {}
       name = row[0]
       category_id = row[1]
       building_id = row[2]
       rating = row[3]
       dic['name'] = name
       dic['category'] = category_id
       dic['building'] = building_id
       dic['rating'] = rating
       output.append(dic)
    return output
    

def barchart_restaurant_categories(db_filename):
    """
    This function accepts a file name of a database as a parameter and returns a dictionary. The keys should be the
    restaurant categories and the values should be the number of restaurants in each category. The function should
    also create a bar chart with restaurant categories along the y-axis and the counts of each category along the
    x-axis.
    """
    source_dir = os.path.dirname(__file__)
    full_path = os.path.join(source_dir, db_filename)
    conn = sqlite3.connect(full_path)
    cur = conn.cursor()
    cur.execute('SELECT categories.category,COUNT(restaurants.category_id) FROM categories JOIN restaurants ON categories.id=restaurants.category_id GROUP BY category ')
    x=cur.fetchall()
    
    dic={}
    for row in x:
        dic[row[0]]=row[1]
    #print(dic)

    y_axis = list(dic.keys())
    x_axis = list(dic.values())


    plt.barh(y_axis,x_axis, color='yellow')
    
    plt.tight_layout()
    plt.title('Types of Restaurants on South University Ave',color='blue')
    plt.ylabel('Restaurant Categories',color='blue')
    plt.xlabel('Number of Restaurants',color='blue')
    plt.xticks([1, 2, 3, 4]) 
    #plt.show()

    return dic




#EXTRA CREDIT
def highest_rated_building(db_filename):#Do this through DB as well
    """
    This function finds the average restaurant rating for each building and returns a tuple containing the
    building number with the highest rated restaurants and the average rating of the restaurants
    in that building. This function should also create a bar chart that displays the buildings along the y-axis
    and their ratings along the x-axis in descending order (by rating).
    """
    source_dir = os.path.dirname(__file__)
    full_path = os.path.join(source_dir, db_filename)

    conn = sqlite3.connect(full_path)
    cur = conn.cursor()
    cur.execute('SELECT buildings.building, restaurants.rating, AVG(restaurants.rating) FROM buildings JOIN restaurants ON buildings.id=restaurants.building_id GROUP BY building')
    x=cur.fetchall()
    
    

#Try calling your functions here
def main():
    pass

class TestHW8(unittest.TestCase):
    def setUp(self):
        self.rest_dict = {
            'name': 'M-36 Coffee Roasters Cafe',
            'category': 'Cafe',
            'building': 1101,
            'rating': 3.8
        }
        self.cat_dict = {
            'Asian Cuisine ': 2,
            'Bar': 4,
            'Bubble Tea Shop': 2,
            'Cafe': 3,
            'Cookie Shop': 1,
            'Deli': 1,
            'Japanese Restaurant': 1,
            'Juice Shop': 1,
            'Korean Restaurant': 2,
            'Mediterranean Restaurant': 1,
            'Mexican Restaurant': 2,
            'Pizzeria': 2,
            'Sandwich Shop': 2,
            'Thai Restaurant': 1
        }
        self.best_building = ((1335, 4.8), ('1335', 4.8))

    def test_get_restaurant_data(self):
        rest_data = get_restaurant_data('South_U_Restaurants.db')
        self.assertIsInstance(rest_data, list)
        self.assertEqual(rest_data[0], self.rest_dict)
        self.assertEqual(len(rest_data), 25)

    def test_barchart_restaurant_categories(self):
        cat_data = barchart_restaurant_categories('South_U_Restaurants.db')
        self.assertIsInstance(cat_data, dict)
        self.assertEqual(cat_data, self.cat_dict)
        self.assertEqual(len(cat_data), 14)

    def test_highest_rated_building(self):
        best_building = highest_rated_building('South_U_Restaurants.db')
        self.assertIsInstance(best_building, tuple)
        self.assertIn(best_building, self.best_building)

if __name__ == '__main__':
    main()
    unittest.main(verbosity=2)