import requests
import json
import os

business_id = os.environ['BUSINESS_ID']

API_KEY = os.environ['API_KEY']
ENDPOINT = 'https://api.yelp.com/v3/businesses/search'
HEADERS = {'Authorization': 'bearer %s' % API_KEY}

data = {}
ids = []
types = ['french', 'indian', 'japanese', 'chinese', 'korean']
for type in types:
    for i in range(0, 1000, 50):
        PARAMETERS = {'term': type + ' restaurant',
                      'limit': 50,
                      'location': 'New York',
                      'offset': i}
        response = requests.get(url=ENDPOINT, params=PARAMETERS, headers=HEADERS)
        temp_data = response.json()
        print("Retrieved data from offset {}".format(i))
        for item in temp_data['businesses']:
            ids.append(item)

    data['businesses'] = ids

    # data = data['businesses'][0]

    f = open(type + "_data.json", mode='w')
    json.dump(data, f)
    f.close()
