import xml.etree.cElementTree as ET
import pprint
import re

def process_map(filename):
    postcodes = set()
    for _, element in ET.iterparse(filename):
        if element.tag == "tag":
            if element.attrib['k'] == 'addr:postcode':
                postcodes.add(element.attrib['v'])
    
    
    return postcodes

def update_postcode(postcodes):
    new_postcodes = set()
    for postcode in postcodes:
        if is_valid_postcode(postcode):
            new_postcode = truncate_postcode(postcode)
            new_postcodes.add(new_postcode)

    return new_postcodes

def is_valid_postcode(postcode):
    if postcode != "Ohio":
        return True

    return False

def truncate_postcode(postcode):
    if len(postcode) > 5:
        new_code = postcode[:5]
        return new_code

    return postcode    

#print(update_postcode(process_map('cleveland.osm')))