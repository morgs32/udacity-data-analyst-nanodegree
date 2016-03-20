#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json

from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017")
db = client.udacity



lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]



# for street names
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Crescent", 'Circle', 'Highway', 'Line', 'North', 'South', 'East', 'West', 'Way',
            'Sideroad']

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")
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


# postal_code

def is_postal_code(elem):
    return (elem.attrib['k'] == "addr:postcode")
non_numeric_re = re.compile(r'\D', re.IGNORECASE)
def is_valid_postal_code(name):
    m = non_numeric_re.search(name)
    # check for letters in postal code
    if m:
        return False
    elif len(name) < 5:
        return False
    else:
        return True





def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        
        node['type'] = element.tag;
        for a in element.attrib:
            if a in CREATED:
                if 'created' not in node:
                    node['created'] = {}
                node['created'][a] = element.attrib[a]
            elif a in ['lat', 'lon']:
                if 'pos' not in node:
                    node['pos'] = [None, None]
                if a == 'lat':
                    node['pos'][0] = float(element.attrib[a])
                else:
                    node['pos'][1] = float(element.attrib[a])
            else:
                node[a] = element.attrib[a]
        
        for tag in element.iter("tag"):
            # if k has problem chars return
            k = tag.attrib['k']
            m = problemchars.search(k)
            if m:
                return
            
            # check k for colon and split 
            m = lower_colon.search(k)
            if m:
                #split k
                keys = k.split(':')
                #check k for addr and make dict
                if keys[0] == 'addr':
                    if 'address' not in node:
                        node['address'] = {}

                    #clean up street names
                    elif is_street_name(tag):
                        # clean first, just like you'll do in data.py
                        street_name = tag.attrib['v']
                        street_name = update_street_type(street_name)
                        street_name = update_cardinal_types(street_name)
                        node['address']['street_name'] = street_name



                    #clean up postal codes
                    elif is_postal_code(tag):
                        postal_code = tag.attrib['v']
                        postal_code = postal_code.strip()
                        postal_code = postal_code[:5]
                        if (is_valid_postal_code(postal_code)):
                            node['address']['postal_code'] = postal_code

                    else:
                        node['address'][keys[1]] = tag.attrib['v']
                else:
                    #just create dict and add keys
                    node[tag.attrib['k']] = tag.attrib['v']
            
            else:
                node[tag.attrib['k']] = tag.attrib['v']
                    


            
        for nd in element.iter("nd"):
            if 'node_refs' not in node:
                node['node_refs'] = []
            node['node_refs'].append(nd.attrib['ref'])

        return node
    else:
        return None


def process_map(file_in, pretty = False):
    # You do not need to change this file
    # file_out = "{0}.json".format(file_in)
    data = []
    db.drop_collection('las_vegas_places')

    # with codecs.open(file_out, "w") as fo:
    for _, element in ET.iterparse(file_in):
        el = shape_element(element)
        if el:
            # data.append(el)
            db.las_vegas_places.insert_one(el)
            # if pretty:
            #     fo.write(json.dumps(el, indent=2)+"\n")
            # else:
            #     fo.write(json.dumps(el) + "\n")

    # return data

def test():
    # NOTE: if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option adds 
    # additional spaces to the output, making it significantly larger.
    process_map('las-vegas_nevada.osm', True)
    # pprint.pprint(data)
    

if __name__ == "__main__":
    test()