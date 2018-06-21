import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import cerberus

import schema
import street_names
import amenities
import postcodes
import city
OSM_PATH = "cleveland.osm"


NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    # YOUR CODE HERE
    
    if element.tag == 'node':
        for item in node_attr_fields:
            node_attribs[item] = element.attrib[item]
        for tag in element:
            tag_dict = {}
            tag_dict['id'] = element.attrib['id']
            tag_dict['value'] = tag.attrib['v']
        
            if PROBLEMCHARS.findall(tag.attrib['k']):
                pass   
            else:
                key_split = tag.attrib['k'].split(":", 1)
                if len(key_split) == 2:
                    tag_dict['type'] = key_split[0]
                    tag_dict['key'] = key_split[1]
                else:
                    tag_dict['type'] = 'regular'
                    tag_dict['key'] = key_split[0]
        
            tags.append(tag_dict)
      
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        for item in way_attr_fields:
            way_attribs[item] = element.attrib[item]
        for idx,tag in enumerate(element):
            if tag.tag == 'tag':
                way_tag_dict = {}
                way_tag_dict['id'] = element.attrib['id']
                way_tag_dict['value'] = tag.attrib['v']
            
                if PROBLEMCHARS.findall(tag.attrib['k']):
                    pass   
                else:
                    key_split = tag.attrib['k'].split(":", 1)
                    if len(key_split) == 2:
                        way_tag_dict['type'] = key_split[0]
                        way_tag_dict['key'] = key_split[1]
                    else:
                        way_tag_dict['type'] = 'regular'
                        way_tag_dict['key'] = key_split[0]
                tags.append(way_tag_dict)
        
            if tag.tag == 'nd':
                nd_dict = {}
                nd_dict['id'] = element.attrib['id']
                nd_dict['node_id'] = tag.attrib['ref']
                nd_dict['position'] = idx
                way_nodes.append(nd_dict)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.items())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))



# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""
    print('starting to open files...')
    with codecs.open(NODES_PATH, 'wt') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'wt') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'wt') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'wt') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'wt') as way_tags_file:

        nodes_writer = csv.DictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = csv.DictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = csv.DictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = csv.DictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = csv.DictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for idx, element in enumerate(get_element(file_in, tags=('node', 'way'))):
            if idx % 1000 == 0:
                print("progress -> {}".format(idx))
            #print("got element: {}".format(element.attrib))
            el = shape_element(element)
            if el:
                #print("if el is true")
                if validate is True:
                    #print("validating...")
                    validate_element(el, validator)
                    #print("validation done.")

                if element.tag == 'node':
                    #print("tag is a node")
                    nodes_writer.writerow(el['node'])
                   
                    for element in el['node_tags']:
                        if element.get('key') == 'street':
                            street_name = element.get('value')
                            updated_name = street_names.update_name(street_name)
                            element['value'] = updated_name
                        
                        elif element.get('key') == 'amenity':
                            amenity_name = element.get('value')
                            updated_amenity = amenities.normalize_amenity(amenity_name)
                            element['value'] = updated_amenity

                        elif element.get('key') == 'postcode':
                            postcode = element.get('value')
                            if not postcodes.is_valid_postcode(postcode):
                                continue

                            updated_postcode = postcodes.truncate_postcode(postcode)
                            element['value'] = updated_postcode

                        elif element.get('key') == 'city':
                            city_name = element.get('value')
                            if not city.is_valid_city(city_name):
                                continue

                        node_tags_writer.writerow(element)

                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=False)
