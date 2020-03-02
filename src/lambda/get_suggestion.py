"""
Read the cuisine from SQS that the user spicify in Lex,
Prepushing all the data into dynamo, creating mapping index on ES
Use as lambda to search id in elastic search, and use it to get data from dynamo
"""
from __future__ import print_function # Python 2/3 compatibility
import json
import random
import urllib3
import boto3


""" ---  Get the cuisine from SQS --- """
QUEUE_NAME = "reservationQ"


def get_cuisine_from_sqs():
    sqs_client = boto3.client('sqs')
    sqs_queue_url = sqs_client.get_queue_url(QueueName=QUEUE_NAME)['QueueUrl']
    response = sqs_client.receive_message(
        QueueUrl=sqs_queue_url,
        MaxNumberOfMessages=1,
        VisibilityTimeout=10,
        WaitTimeSeconds=10,
    )
    if response:
        body = response['Messages'][0]['Body']
        data = json.loads(body)
        return data['rType']
    else:
        print("Cannot get the data from sqs")
        return None


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


if __name__ == '__main__':

    """ 0. get cuisine from sqs"""
    cuisine = get_cuisine_from_sqs()

    """ 1. get es data """
    count = get_esquery_count(cuisine)
    start = random.randrange(count - ES_SEARCH_RESULT_SIZE - 1)
    data = get_esquery_data(cuisine, start)
    hits = data['hits']['hits']
    ids = get_id_from_hits(hits)

    """ 2. get dynamo data """
    restaurants = get_dbdetail_by_id(ids)
