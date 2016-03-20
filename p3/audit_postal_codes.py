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
non_numeric_re = re.compile(r'\D', re.IGNORECASE)




def audit_postal_code(postal_codes, postal_code):
    m = non_numeric_re.search(postal_code)

    # check for dashes
    if postal_code.find('-') != -1:
        postal_codes['dash'].add(postal_code)

    # check for letters in postal code
    elif m:
        postal_codes['letters'].add(postal_code)

    # check for length
    elif len(postal_code) > 5:
        postal_codes['length'].add(postal_code)

def is_valid_postal_code(name):
    m = non_numeric_re.search(postal_code)
    # check for letters in postal code
    if m:
        return false
    elif len(name) < 5:
        return false
    else:
        return true



    return name

def is_postal_code(elem):
    return (elem.attrib['k'] == "addr:postcode")


def audit(osmfile):
    osm_file = open(osmfile, "r")

    file_out = "audit_postal_code.json";

    postal_codes = defaultdict(set)

    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_postal_code(tag):
                    postal_code = tag.attrib['v']
                    postal_code = postal_code.strip()
                    postal_code = postal_code[:5]
                    if (is_valid_postal_code(postal_code))
                        audit_postal_code(postal_codes, postal_code)
    osm_file.close()

    for s in postal_codes:
        postal_codes[s] = list(postal_codes[s])

    with codecs.open(file_out, "w") as fo:
        fo.write(json.dumps(postal_codes, indent=2)+"\n")

    return postal_codes





def test():
    st_types = audit(OSMFILE)



if __name__ == '__main__':
    test()