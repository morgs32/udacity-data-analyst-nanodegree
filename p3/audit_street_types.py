"""
Your task in this exercise has two steps:

- audit the OSMFILE and change the variable 'mapping' to reflect the changes needed to fix 
    the unexpected street types to the appropriate ones in the expected list.
    You have to add mappings only for the actual problems you find in this OSMFILE,
    not a generalized solution, since that may and will depend on the particular area you are auditing.
- write the update_name function, to actually fix the street name.
    The function takes a string with street name as an argument and should return the fixed name
    We have provided a simple test so that you see what exactly is expected
"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import codecs
import json

OSMFILE = "sample.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Crescent", 'Circle', 'Highway', 'Line', 'North', 'South', 'East', 'West', 'Way',
            'Sideroad']


mapping = { "St": "Street",
            "St.": "Street",
            'Ave': 'Avenue',
            'Rd': 'Road',
            'dr': 'Drive',
            'DR': 'Drive',
            'Rd.': 'Road',
            'Dr': 'Drive',
            'Dr.': 'Drive',
            'Ct': 'Court',
            'Ct.': 'Court',
            'Blvd': 'Boulevard',
            'Blvd.': 'Boulevard',
            "E" : "East",
            "E." : "East",
            "N" : "North",
            "N." : "North",
            "S" : "South",
            "S." : "South",
            "W" : "West",
            "W." : "West"
            }
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
def update_street_type(name):
    m = street_type_re.search(name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            # replace street type in street_name
            if street_type in mapping:
                name = re.sub(street_type_re, mapping[street_type], name)
    return name

map_cardinal_directions = {
    "E" : "East",
    "E." : "East",
    "N" : "North",
    "N." : "North",
    "S" : "South",
    "S." : "South",
    "W" : "West",
    "W." : "West"
}
bad_directions = "|".join(map_cardinal_directions.keys()).replace('.', '')
cardinal_dir_updater_re = re.compile(r'\b(' + bad_directions + r')\b\.?', re.IGNORECASE)
def update_cardinal_types(name):
    m = cardinal_dir_updater_re.search(name)
    if m:
        cardinal_dir = m.group()
        if cardinal_dir in mapping:
            name = re.sub(cardinal_dir_updater_re, map_cardinal_directions[cardinal_dir], name)
    return name


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

cardinal_dir_re = re.compile(r'^[NSEW]\b\.?', re.IGNORECASE)
def audit_cardinal_dir(cardinal_dirs, street_name):
    m = cardinal_dir_re.search(street_name)
    if m:
        cardinal_dir = m.group()
        cardinal_dirs[cardinal_dir].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")


    street_types_file_out = "audit_street_types.json"
    street_types = defaultdict(set)
    
    cardinal_dirs_file_out = 'audit_cardinal_dirs.json'
    cardinal_dirs = defaultdict(set)

    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    # clean first, just like you'll do in data.py
                    street_name = tag.attrib['v']
                    street_name = update_street_type(street_name)
                    street_name = update_cardinal_types(street_name)
                    audit_street_type(street_types, street_name)
                    audit_cardinal_dir(cardinal_dirs, street_name)

    osm_file.close()

    for s in street_types:
        street_types[s] = list(street_types[s])
    with codecs.open(street_types_file_out, "w") as fo:
        fo.write(json.dumps(street_types, indent=2)+"\n")


    for s in cardinal_dirs:
        cardinal_dirs[s] = list(cardinal_dirs[s])
    with codecs.open(cardinal_dirs_file_out, "w") as fo:
        fo.write(json.dumps(cardinal_dirs, indent=2)+"\n")

    return street_types



def test():
    st_types = audit(OSMFILE)
    pprint.pprint(dict(st_types))



if __name__ == '__main__':
    test()