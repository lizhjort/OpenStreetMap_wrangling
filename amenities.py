import xml.etree.cElementTree as ET
import pprint
import re

def process_map(filename):
    amenities = set()
    for _, element in ET.iterparse(filename):
        if element.tag == "tag":
            if element.attrib['k'] == 'amenity':
                amenities.add(element.attrib['v'])
    return amenities
    
def update_amenities(amenities):
    new_amenities = set()
    for amenity in amenities:   
        new_amenities.add(normalize_amenity(amenity))
    return new_amenities

def normalize_amenity(amenity):
    result = amenity.lower()
    result = result.replace(" ", "_")
    return result
    

#print(update_amenities(process_map('cleveland.osm')))    
