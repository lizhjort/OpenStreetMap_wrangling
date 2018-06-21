import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "cleveland.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Center", "North", "Northeast", "Northwest", "Southeast", 
            "South", "West", "East", "Circle", "Way",  ]

# UPDATE THIS VARIABLE
MAPPING = { "St": "Street",
            "St.": "Street",
            "Ave": "Avenue",
            "Ave.": "Avenue",
            "ave": "Avenue",
            "Rd.": "Road",
            "Rd": "Road",
            "Esplanade": "Road",
            "Blvd": "Boulevard",
            "Blvd.": "Boulevard",
            "Dr": "Drive",
            "Cedar": "Cedar Road",
            "Arlington": "Arlington Road",
            "Lorain": "Lorain Road",
            "Middleton": "Middleton Road",
            "Clair": "Clair Avenue",
            "Engel": "Engel Road",
            "Fairmount": "Fairmount Boulevard",
            "Fleet": "Fleet Avenue",
            "Paula": "Paula Drive",
            "Rauscher": "Rauscher Court",
            "Lee": "Lee Avenue",
            "Mayfield": "Mayfield Road",
            "SE": "Southeast",
            "SW": "Southwest",
            "NE": "Northeast",
            "NW": "Northwest",
            "N": "North",
            "S": "South",
            "E": "East",
            "W": "West",

}
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


def update_name(original_street_name, mapping=MAPPING):
    split_name = original_street_name.split(" ")
    abbr_street = split_name[-1]
    name = original_street_name
    if abbr_street in mapping:
        name = " ".join(split_name[:-1] + [mapping[abbr_street]])
    return name

