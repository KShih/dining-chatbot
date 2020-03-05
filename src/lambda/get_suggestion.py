"""
Read the cuisine from SQS that the user spicify in Lex,
Prepushing all the data into dynamo, creating mapping index on ES
Use as lambda to search id in elastic search, and use it to get data from dynamo
"""
from __future__ import print_function  # Python 2/3 compatibility
import json
import random
import urllib3
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

""" ---  Get the id from es --- """
ENDPOINT = "https://search-restaurants-kcmb5vcpfi2wp6m25xvuy2ht5m.us-east-1.es.amazonaws.com/"
INDEX = "restaurants/"
ES_SEARCH_RESULT_SIZE = 10  # the size of the data we expect to be returned from es, set it little to ease the server loading


def get_esquery_count(cuisine):
    base_url = ENDPOINT+INDEX
    count_url = base_url + '_count?q=' + cuisine
    try:
        http = urllib3.PoolManager()
        result = http.request('GET', count_url).data  # result is binary data
        data = json.loads(result.decode('utf-8'))
        return data['count']
    except:
        return None


def get_esquery_data(cuisine, start):
    base_url = ENDPOINT + INDEX
    search_url = base_url + '_search?q=' + cuisine + "&from=" + str(start) + "&size=" + str(ES_SEARCH_RESULT_SIZE)
    try:
        http = urllib3.PoolManager()
        result = http.request('GET', search_url).data  # result is binary data
        data = json.loads(result.decode('utf-8'))
        return data
    except:
        return None


def get_id_from_hits(hits):
    return [hit['_source']['id'] for hit in hits]


""" ---  Get the data from dynamo --- """


def get_dbdetail_by_id(ids):
    client = boto3.client('dynamodb')
    restaurants = []

    for id in ids:
        data = client.get_item(TableName='yelp-restaurants',
                               Key={
                                   'id': {'S': id}
                               })
        data = data['Item']
        name, address, rating, phone = "", "", "", ""
        if 'name' in data:
            name = data['name']['S']
        if 'address' in data:
            address = data['address']['S']
        if 'rating' in data:
            rating = data['rating']['S']
        if 'phone' in data:
            phone = data['phone']['S']
        restaurants.append([name, address, rating, phone])

    restaurants.sort(key=lambda x:x[2], reverse=True)  # sort by rating
    return restaurants


""" ---  Build and send message ---"""


def build_msg(restaurants, time, people):
    base = "Top suggestions for {} people, for today at {}. ".format(people, time)
    res_msg = ""
    flag, i = True, 0
    while flag and i < 3:
        temp = "{name} located at {address}. \n {phone}\n".format(name=restaurants[i][0], address=restaurants[i][1], phone=restaurants[i][-1])
        if len(temp) + len(base) < 160:
            base += temp
            i += 1
        else:
            flag = False
    return base


def send_sns(msg, phone_num):
    sns_client = boto3.client('sns')
    if len(phone_num) < 10:
        print("Phone Number error, cannot send SNS")
    elif len(phone_num) == 10:
        phone_num = "1" + phone_num

    response = sns_client.publish(
        PhoneNumber=phone_num,
        Message=msg
    )

def lambda_handler(event, context):
    print(">>>>>>>> Get suggestions being triggered <<<<<<<<<")
    """ 0. get cuisine from sqs"""
    plain_data_sqs = event['Records'][0]['body']  # trigger by sqs
    data_sqs = json.loads(plain_data_sqs)
    cuisine = data_sqs['rType']

    """ 1. get es data """
    count = get_esquery_count(cuisine)
    start = random.randrange(count - ES_SEARCH_RESULT_SIZE - 1)
    data = get_esquery_data(cuisine, start)
    hits = data['hits']['hits']
    ids = get_id_from_hits(hits)

    """ 2. get dynamo data """
    restaurants = get_dbdetail_by_id(ids)

    """ 3. send sns """
    msg = build_msg(restaurants, data_sqs['rTime'], data_sqs['rPeople'])
    send_sns(msg, data_sqs['PhoneNumber'])
    print(">>>>>>>> Get suggestions finished <<<<<<<<<")