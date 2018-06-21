import xml.etree.cElementTree as ET
import pprint
import re

expected = ["Kent", "Peninsula", "Akron", "Newton Falls", "Bedford", "North Olmsted", "Warrensvill Heights", "Berlin Center", "Streetsboro", 
            "Wooster", "Cleveland Heights", "Shaker Heights", "Beachwood", "Ravenna", "Champion", "Alliance", "Wellington", 
            "Cuyahoga Falls", "Middleburg Hts.", "Lagrange", "Brooklyn", "Cleveland", "Richmond Heights", "Strongsville", "Norton", "Geneva", 
            "Euclid", "Canton", "Wickliffe", "Massillon", "Maple Heights", "Kirtland", "Lyndhurst", "Lakewood", "Wadsworth", "Fairview Park", 
            "Berea", "Hudson", "Chesterland", "Woodmere", "Parma", "Mayfield Heights", "North Canton" ]

def process_map(filename):
    cities = set()
    for _, element in ET.iterparse(filename):
        if element.tag == "tag":
            if element.attrib['k'] == 'addr:city':
                cities.add(element.attrib['v'])
    
    
    return cities
    
def update_city_list(cities):
    city_list = set()
    for city in cities:
        if is_valid_city(city):
            city_list.add(city)
    return city_list

def is_valid_city(city):
    if city not in expected:
        return False

    return True


#print(update_city_list(process_map('cleveland.osm')))    
