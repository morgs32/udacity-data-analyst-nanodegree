# Project 3: OpenStreetMap Project - Data Wrangling with MongoDB


Map Area: Las Vegas Nevada
https://mapzen.com/data/metro-extracts/
(search for Salt Lake City)

[Link to Google Maps](https://www.google.com/maps/place/Salt+Lake+City,+UT/@40.7765233,-112.0605694,11z/data=!3m1!4b1!4m2!3m1!1s0x87523d9488d131ed:0x5b53b7a0484d31ca)

I chose Las Vegas Nevada. I supposed the data would be incomplete but we some interesting things turn up among most common churches (places to elope?), restaurants, and other destinations.
Originally, I had chosen Detroit but there was far too much data (~1gb).

I created a small sample size of the Las Vegas area using the [sample.py](./samply.py) script.

##1. Problems Encountered in the Map


### Street Names

The [audit_street_type.py](./audit_street_type.py) script creates a .json file containing a dictionary of unexpected street types. Running it for the first time created [audit_street_types[original].json](./audit_street_types[original].json)
And after reviewing the .json file (saved in its original form), I added some street types to the list of those that are expected:
```
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", 
    "Place", "Square", "Lane", "Road", 
    "Trail", "Parkway", "Commons", "Crescent", 'Circle', 
    'Highway', 'Line', 'North', 'South', 'East', 'West', 'Way',
    'Sideroad']
```

I also added to the list of street type mappings (from abbreviated to unabbreviated):
```
mapping = { "St": "Street",
            "St.": "Street",
            'Ave': 'Avenue',
            'Rd.': 'Road',
            'Dr': 'Drive',
            'Dr.': 'Drive',
            'Ct': 'Court',
            'Ct.': 'Court',
            'Blvd': 'Boulevard',
            'Blvd.': 'Boulevard'
            }
```

Finally, I set about replacing abbreviations for cardinal directions at the beginning of street names: (ie. replacing “W Eight Mile" with "West Eight Mile").
An audit of my sample set, again using [] produced this result, captured in [audit_cardinal_dirs[original]](./audit_cardinal_dirs[original].json)
```
{
  "S": [
    "S Grand River Ave"
  ], 
  "E.": [
    "E. Jefferson Ave", 
    "E. Fisher Service Dr"
  ], 
  "E": [
    "E Huron River Drive", 
    "E C Row Avenue", 
    "E Big Beaver Rd", 
    "E 4th St.", 
    "E Long Lake Rd"
  ], 
  "W": [
    "W Big Beaver Rd", 
    "W Boston Blvd", 
    "W Grand River", 
    "W Eight Mile", 
    "W 7 Mile Rd", 
    "W Long Lake Rd"
  ]
}
```

I incorporated methods that would update street names into [data.py](./data.py), the script used to move the data into mongodb.


### Postal Codes
The [audit_postal_code.py](./audit_postal_code.py) script creates a .json file containing a dictionary of unexpected postal codes. Running it for the first time created [audit_postal_codes[original].json](./audit_postal_codes[original].json)
```
{
  "dash": [
    "48095-2555", 
    "48131-9572", 
    "48178-8798"
  ], 
  "length": [
    "481241"
  ], 
  "letters": [
    "N7T 7B4", 
    "MI 48170", 
    ...
  ]
}
```
I categorized unexpected postal codes by whether they included a '-' (dash) sign, or were longer or shorter than 5 digits, or contained letters.

When moving the open street map entries to mongodb, I did not transfer any tags with letters in the postal code. I also truncated all postal codes to 5 in length. If any were shorter than 5 digits long, the tag was again ignored.

I incorporated all this into [data.py](./data.py), the script used to move the data into mongodb.


## Data Overview

This section contains basic statistics about the dataset and the MongoDB queries used to gather them.
                                                
###File sizes
las-vegas_nevada.osm ......... 187.2 MB
                                                
###Number of documents                                          
```
db.las_vegas_places.find().count()
930541
```

###Number of nodes                                             
```
db.las_vegas_places.find({"type":"node"}).count()
837156
```

###Number of ways
```
db.las_vegas_places.find({"type":"way"}).count()
93223
```

###Number of unique users                                            
```
db.las_vegas_places.distinct("created.user").length
781
```

###Top 1 contributing user
```
db.las_vegas_places.aggregate([ {"$group":{"_id":"$created.user", "count":{"$sum":1}}}, {"$sort": {count: -1}} , {"$limit":3}  ])
{ "_id" : "alimamo", "count" : 253804 }
```

###Number of users appearing only once (having 1 post)
```
db.las_vegas_places.aggregate([{"$group":{"_id":"$created.user", "count":{"$sum":1}}}, {"$group":{"_id":"$count", "num_users":{"$sum":1}}}, {"$sort":{"_id":1}}, {"$limit":1}])
{ "_id" : 1, "num_users" : 152 }
```
“_id” represents postcount



## Additional Ideas
Additional data exploration using MongoDB queries
                                                
###Top 10 appearing amenities
```
db.las_vegas_places.aggregate([{"$match":{amenity:{"$exists":1}}}, {"$group": {_id:"$amenity", count:{"$sum":1}}}, {"$sort": {count: 1}}, {"$limit":10}] )
```
Returned:
```                                                
{ "_id" : "marketplace", "count" : 1 }
{ "_id" : "swingerclub", "count" : 1 }
{ "_id" : "mall", "count" : 1 }
{ "_id" : "lounge", "count" : 1 }
{ "_id" : "adult day care", "count" : 1 }
{ "_id" : "koolsville tattoo", "count" : 1 }
{ "_id" : "whirlpool", "count" : 1 }
{ "_id" : "food_court", "count" : 1 }
{ "_id" : "self_storage", "count" : 1 }
{ "_id" : "finish line", "count" : 1 }
```

###Biggest religion (no surprise here)
```
db.las_vegas_places.aggregate([{"$match" : {"amenity" : "place_of_worship"}}, {"$group" : {"_id" : {"religion" : "$religion", "denomination" : "$denomination"}, "count" : {"$sum" : 1}}}, {"$sort" : {"count" : -1}}, {"$limit": 10}])

```
Returned:
```
{ "_id" : { "religion" : "christian" }, "count" : 201 }
{ "_id" : { "religion" : "christian", "denomination" : "baptist" }, "count" : 50 }
{ "_id" : { "religion" : "christian", "denomination" : "mormon" }, "count" : 26 }
{ "_id" : { "religion" : "christian", "denomination" : "catholic" }, "count" : 17 }
{ "_id" : { "religion" : "christian", "denomination" : "lutheran" }, "count" : 16 }
{ "_id" : { "religion" : "christian", "denomination" : "jehovahs_witness" }, "count" : 11 }
{ "_id" : { "religion" : "christian", "denomination" : "pentecostal" }, "count" : 9 }
{ "_id" : {  }, "count" : 6 }
{ "_id" : { "religion" : "christian", "denomination" : "methodist" }, "count" : 6 }
{ "_id" : { "religion" : "christian", "denomination" : "presbyterian" }, "count" : 6 }
```
Interestingly, there are a fair number of churchase for jehovahs witness.
And, you can't tell how how many churches might be for 24hour marriage parlors.

###Most popular cuisines

```
db.las_vegas_places.aggregate([{"$match":{"amenity":{"$exists":1}, "amenity":"restaurant"}}, {"$group":{"_id":"$cuisine", "count":{"$sum":1}}}, {"$sort":{"count":-1}}, {"$limit":2}])
```
Returned:
```
{ "_id" : null, "count" : 138 }
{ "_id" : "mexican", "count" : 24 }
```
The fact that the most common cuisine is null is a testament to data quality problems.



##Resources used:
- For inserting documents into mongodb: https://docs.mongodb.org/getting-started/python/insert/
- Various python questions: https://docs.python.org/2/tutorial/inputoutput.html
- https://developers.google.com/places/web-service/search
- https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet#links
- https://docs.google.com/document/d/1F0Vs14oNEs2idFJR3C_OPxwS6L0HPliOii-QpbmrMo4/pub?embedded=True

              
##Conclusion                        
The Open Street Maps data set for Las Vegas is clearly incomplete and could use a good deal of cleaning. For example, the 66 restaurants that don't have a designated type of cuisine. 

I would like to compare data in a search of restaurants in a certain radius using Google's Places API and Open Street Map data to see roughly how much more information Google has. Obviously, Google has a clear advantage in that restaurant and business owners want to make sure their information is up to date on Google, so that their businesses are easier for customers to find online. Google also has an expanding community of active contributors (Google Local Guides) that are incentivized by prizes and prowess to continuously update and add information for Google Places.

How would I go about it?
According to the documentation here, for Google Places:
https://developers.google.com/places/web-service/search
I would start with the center of Las Vegas in lon/lat. Going to maps.google.com, I estimated the center was approximately here: 36.175373, -115.168482
Using this tool: http://www.mapdevelopers.com/draw-circle-tool.php
I put in the center lat/lon above, and 10 miles seemed like a radius that encapsulated most of the city.

This would obviously return a ton of results even if we searched just for restaurants. A couple problems with this approach:
1. Google api limits. We would probably have to spread our search over a couple days, because google limits the number of times you can use the api per day.

A comparison of data would just count the number of restaurants (or churches, or casinos) in the Open Street Map data set vs the Google Places data set. A simple bar chart would do.

I would not be interested in updating Open Street Map data. It would seem futile. Better to use Google Places data as a substitute, if we could successfully export a copy of the data into our own databases. Especially since Google has much more information about a place, for example: reviews and ratings (zagat ratings), and hours (we would probably see a lot more 24 hour venues than almost anywhere else in the world).





















