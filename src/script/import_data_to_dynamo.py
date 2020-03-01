from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import os
from datetime import datetime

def buildItem(data, cuisine):
    item = {}
    if 'id' in data:
        item['id'] = {'S': data['id']}
    if 'name' in data:
        item['name'] = {'S': data['name']}
    if 'url' in data:
        item['url'] = {'S': data['url']}
    if 'rating' in data:
        item['rating'] = {'S': str(data['rating'])}
    if 'coordinates' in data:
        item['location'] = {'SS': [str(data['coordinates']['latitude']), str(data['coordinates']['longitude'])]}
    if 'price' in data:
        item['price'] = {'S': data['price']}
    if 'address' in data:
        item['address'] = {'S': data['display_address']}
    if 'phone' in data:
        item['phone'] = {'S': data['phone']}
    item['cuisine'] = {'S': cuisine}
    item['timestamp'] = {'S': str(datetime.timestamp(datetime.now()))}
    return item


dynamodb = boto3.client('dynamodb')

# table = dynamodb.Table('restaurants')

fnames = os.listdir("../yelp_data")

failCount, passCount = 0, 0
for name in fnames:
    fname = os.path.join("../yelp_data", name)
    print(fname)
    cuisine = name.split('_')[0]
    print(fname, cuisine)
    with open(fname, 'r') as json_file:
        restaurants = json.load(json_file)['businesses']

        for i, restaurant in enumerate(restaurants):
            if not restaurant['is_closed']:
                item = buildItem(restaurant, cuisine)
                print(item)
                try:
                    dynamodb.put_item(TableName='yelp-restaurants', Item=item)
                    passCount += 1
                except:
                    print("Failed")
                    failCount += 1
            print("Processed: {} of {}".format(i, cuisine))

print("Pass Count: ", passCount)
print("Fail Count: ", failCount)
